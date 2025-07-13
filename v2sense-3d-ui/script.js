let scene, camera, renderer;
let vehicles = [];

fetch('data.json')
  .then(res => res.json())
  .then(data => {
    init(data);
    animate();
  });

function init(vehicleData) {
  // Scene setup
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.z = 200;

  renderer = new THREE.WebGLRenderer();
  renderer.setSize(window.innerWidth, window.innerHeight * 0.9);
  document.getElementById('radarCanvas').appendChild(renderer.domElement);

  // Radar grid (circle)
  const circle = new THREE.RingGeometry(95, 100, 64);
  const circleMat = new THREE.MeshBasicMaterial({ color: 0x00ff00, side: THREE.DoubleSide });
  const ring = new THREE.Mesh(circle, circleMat);
  ring.rotation.x = Math.PI / 2;
  scene.add(ring);

  // Vehicles as spheres
  vehicleData.forEach(v => {
    const geo = new THREE.SphereGeometry(3, 16, 16);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ffff });
    const sphere = new THREE.Mesh(geo, mat);
    sphere.userData = {
      speed: v.speed,
      angle: v.angle * (Math.PI / 180),
    };
    sphere.position.set(v.x, 0, v.y);
    scene.add(sphere);
    vehicles.push(sphere);
  });
}

function animate() {
  requestAnimationFrame(animate);

  vehicles.forEach(vehicle => {
    const dx = vehicle.userData.speed * 0.1 * Math.cos(vehicle.userData.angle);
    const dz = vehicle.userData.speed * 0.1 * Math.sin(vehicle.userData.angle);
    vehicle.position.x += dx;
    vehicle.position.z += dz;
  });

  renderer.render(scene, camera);
}
