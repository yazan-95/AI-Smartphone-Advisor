import json
import logging
import traceback
import re

from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static

from ai_engine.recommender.recommender_engine import recommend as hybrid_recommend
from ai_engine.recommender.embedding_engine import EmbeddingSmartphoneRecommender
from ai_engine.recommender.satisfaction_engine import SatisfactionRecommender
from ai_engine.recommender.data_loader import load_assets
from ai_engine.recommender.explainability import explain_recommendation

logger = logging.getLogger(__name__)

# -------------------------------------------------
# LOAD DATASET ONCE (SAFE)
# -------------------------------------------------
assets = load_assets()
raw_df = assets.get("raw_df")


# -------------------------------------------------
def index(request):
    return render(request, "index.html")


# -------------------------------------------------
def normalize_user_input(data: dict) -> dict:
    return {
        "brand": (data.get("brand") or "").strip(),
        "price": float(data.get("price") or 0),
        "cam_resolution": float(data.get("camera") or 0),
        "battery": float(data.get("battery") or 0),
        "ram": float(data.get("ram") or 0),
        "display_size": float(data.get("display_size") or 0),
        "weight": float(data.get("weight") or 0),
        "release_year": int(data.get("release_year") or 0),
        "performance_profile": data.get("performance", "balanced"),
    }


# -------------------------------------------------
def is_cold_start(user_input: dict) -> bool:
    numeric_fields = [
        "price", "cam_resolution", "battery",
        "ram", "display_size", "weight", "release_year"
    ]
    return all(user_input.get(f, 0) == 0 for f in numeric_fields)


# -------------------------------------------------
def derive_base_model(model_name: str) -> str:
    if not model_name:
        return ""
    return re.sub(r"\b\d+\s?(GB|TB)\b", "", model_name, flags=re.I).strip()


# -------------------------------------------------
@require_POST
def recommend(request):
    try:
        payload = json.loads(request.body or "{}")
        raw_mode = (payload.get("mode") or "classic").lower()
        mode = "hybrid" if raw_mode in ("classic", "hybrid") else raw_mode

        user_input = normalize_user_input(payload)

        if raw_df is None or raw_df.empty:
            return JsonResponse(
                {"results": [], "error": "Dataset unavailable"},
                status=200
            )

        # -----------------------------------------
        # FILTER DATASET (SOFT CONSTRAINTS)
        # -----------------------------------------
        df_pool = raw_df.copy()

        if user_input["brand"]:
            df_pool = df_pool[
                df_pool["brand"].str.lower() == user_input["brand"].lower()
            ]

        if user_input["price"] > 0:
            lower = user_input["price"] * 0.7
            upper = user_input["price"] * 1.3
            df_pool = df_pool[
                (df_pool["price"] >= lower) &
                (df_pool["price"] <= upper)
            ]

        if user_input["release_year"] > 0:
            df_pool = df_pool[
                df_pool["release_year"] >= user_input["release_year"] - 2
            ]

        if df_pool.empty:
            return JsonResponse({
                "engine_mode": mode,
                "results": [],
                "brand_info": {
                    "error": "No phones found for this brand and price range",
                    "suggestion": raw_df["brand"]
                        .value_counts()
                        .head(5)
                        .index
                        .tolist()
                }
            }, status=200)

        # -----------------------------------------
        # REMOVE STORAGE VARIANTS
        # -----------------------------------------
        df_pool = (
            df_pool
            .assign(base_model=df_pool["model"].apply(derive_base_model))
            .drop_duplicates(subset=["base_model"])
        )

        # -----------------------------------------
        # ENGINE SELECTION
        # -----------------------------------------
        cold_start = is_cold_start(user_input)

        if cold_start and mode == "hybrid":
            df = df_pool.sort_values(
                "release_year", ascending=False
            ).head(5)

            result_items = df.assign(
                match_score=0.5,
                feature_scores=[{}] * len(df)
            ).to_dict("records")

        else:
            if mode == "hybrid":
                engine_result = hybrid_recommend(user_input, top_n=5)
                result_items = engine_result.get("items", [])

            elif mode == "semantic":
                semantic_engine = EmbeddingSmartphoneRecommender(df_pool)
                df = semantic_engine.recommend(
                    payload.get("nl_query", ""),
                    top_n=5
                )
                result_items = df.to_dict("records")

            elif mode == "satisfaction":
                satisfaction_engine = SatisfactionRecommender(df_pool)
                df = satisfaction_engine.recommend(user_input, top_n=5)
                result_items = df.to_dict("records")

            else:
                result_items = []

        # -----------------------------------------
        # BUILD FRONTEND RESPONSE
        # -----------------------------------------
        response_items = []

        for item in result_items:
            model_name = item.get("model")
            if not model_name:
                continue

            try:
                full_row = raw_df.loc[
                    raw_df["model"] == model_name
                ].iloc[0]
            except Exception:
                continue

            explanation = explain_recommendation(
                item.get("feature_scores", {})
            )

            response_items.append({
                "brand": full_row.get("brand"),
                "model": model_name,
                "score": round(
                    float(item.get("match_score", 0)), 3
                ),
                "why": explanation.get("top_features", []),
                "pros": explanation.get("pros", []),
                "cons": explanation.get("cons", []),
                "specs": {
                    "price": full_row.get("price"),
                    "camera": full_row.get("cam_resolution"),
                    "battery": full_row.get("battery"),
                    "ram": full_row.get("ram"),
                    "display": (
                        f'{full_row.get("display_size", "?")}" '
                        f'{full_row.get("display_type", "")}'
                    ),
                    "five_g": bool(full_row.get("has_5g", False)),
                    "year": int(full_row.get("release_year", 0)),
                },
                # Always return the symbolic 3D model
                "3d_model_url": static(
                    "recommender_app/models/device_phone.glb"
                ),
            })

        return JsonResponse({
            "engine_mode": mode,
            "performance_profile": user_input.get("performance_profile"),
            "cold_start_used": cold_start,
            "results": response_items
        }, status=200)

    except Exception as e:
        logger.error(
            f"Recommendation failure: {str(e)}\n{traceback.format_exc()}"
        )
        return JsonResponse(
            {"results": [], "error": "Safe recommendation failure"},
            status=200
        )


# -------------------------------------------------
@require_GET
def check_3d_status(request, model_slug):
    return JsonResponse({"status": "disabled"}, status=200)
