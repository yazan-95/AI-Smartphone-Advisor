// Use ES modules from CDN
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.module.js";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.158.0/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "https://cdn.jsdelivr.net/npm/three@0.158.0/examples/jsm/loaders/GLTFLoader.js";

// -------------------------
// Container
// -------------------------
const container = document.getElementById("phone3D");
if (!container) {
    console.error("Container #phone3D not found!");
}

// -------------------------
// Scene
// -------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf4f4f4);

// -------------------------
// Camera
// -------------------------
const camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / container.clientHeight,
    0.1,
    100
);
camera.position.set(0, 1.5, 3);

// -------------------------
// Renderer
// -------------------------
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

// -------------------------
// Lights
// -------------------------
const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
dirLight.position.set(2, 4, 2);
scene.add(dirLight);

// -------------------------
// Controls
// -------------------------
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

// -------------------------
// Load default GLB model
// -------------------------
const loader = new GLTFLoader();
const defaultModelPath = "/static/recommender_app/models/phone.glb";

let phoneModel = null;

function loadPhoneModel(path) {
    // Remove previous model
    if (phoneModel) {
        scene.remove(phoneModel);
        phoneModel.traverse(obj => {
            if (obj.isMesh) obj.geometry.dispose();
        });
        phoneModel = null;
    }

    loader.load(
        path,
        (gltf) => {
            phoneModel = gltf.scene;
            phoneModel.rotation.y = Math.PI / 6;
            scene.add(phoneModel);
        },
        (xhr) => {
            // Optional: progress feedback
            console.log(`3D model loading: ${(xhr.loaded / xhr.total * 100).toFixed(1)}%`);
        },
        (error) => {
            console.error("Error loading 3D model:", error);
        }
    );
}

// Load default model initially
loadPhoneModel(defaultModelPath);

// -------------------------
// Window resize handling
// -------------------------
window.addEventListener("resize", () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

// -------------------------
// Animate
// -------------------------
function animate() {
    requestAnimationFrame(animate);

    if (phoneModel) {
        phoneModel.rotation.y += 0.002; // slow auto-rotate
    }

    controls.update();
    renderer.render(scene, camera);
}

animate();

// -------------------------
// Expose loader for dynamic 3D replacement
// -------------------------
window.loadPhoneModel = loadPhoneModel;
