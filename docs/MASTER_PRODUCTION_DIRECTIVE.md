# CODECITY: LIVING WORLD
## Updated Master Production Directive

Repository: `zaydattique/codecity`

Continue development from the existing repository and current Phase A checkpoint.

Act as the lead game developer, technical director, AI engineer, 3D technical artist, environment artist, character animator, audio engineer and quality assurance engineer.

This is a serious university-level interactive game and artificial intelligence project. The final product must feel like a professionally developed standalone open-world game rather than a basic simulation, educational website or collection of primitive 3D objects.

GTA V is the visual and gameplay quality reference. GTA VI is the inspiration for natural environmental responsiveness and NPC behavior. Do not copy proprietary assets, characters, maps, branding or source code.

## 01. Inspect and preserve existing work

Before making changes:

- Inspect the latest main branch, active branches, open pull requests, commits, workflows and existing artifacts.
- Read AGENTS.md, ARCHITECTURE.md, ROADMAP.md, HISTORY.md, PERFORMANCE.md, ASSET_REGISTRY.md, THIRD_PARTY_NOTICES.md, FILEMAP.md and all production instructions.
- Inspect the existing Blender automation, MPFB character pipeline, Poly Haven intake pipeline and Python worker.
- Determine exactly what Phase A completed and which acceptance gates remain open.
- Do not duplicate functioning implementations.
- Resolve failed workflows, rendering failures, missing dependencies and incomplete implementation.
- Preserve useful existing automation and source provenance.
- Update conflicting documentation to reflect the new dual-mode direction.

Existing foundation, rendering tools and character pipelines must be improved rather than discarded without technical justification.

## 02. Updated game architecture: two playable modes

CodeCity must contain two independent gameplay modes sharing the same high-quality city, characters, animation system, physics, vehicles, NPC intelligence, weather, audio and interaction systems.

### Mode A: Living World

A story-driven open-world game containing:

- Free-roam exploration.
- Cinematic story missions.
- Walking, driving and environmental interactions.
- Autonomous NPC behavior.
- Character relationships.
- Dynamic encounters.
- Jobs and activities.
- Persistent player progress.
- Branching story outcomes.

This mode must not force educational exercises on the player.

### Mode B: CodeCity Academy

A mission-based educational game set inside the same city.

Teach genuine Python programming through physical world interactions, city systems, automation and problem-solving.

Do not create conventional educational cards, childish quizzes or a separate boring dashboard.

Education must be experienced through the game.

Academy missions should have separate progression, checkpoints, learning achievements and save data while reusing shared engine systems.

The player must be able to switch modes from the main menu without losing progress.

## 03. Academy curriculum and physical learning missions

Implement a structured progression from beginner to advanced Python.

### Mission 01: Control Room

Teach print statements, comments and basic syntax.

Player visits an operational control room and sends messages to actual electronic displays installed around the city.

The displays must update based on executed Python output.

### Mission 02: Resource Manager

Teach variables and data types.

Player manages warehouse stock, equipment quantities, fuel, money and supply deliveries.

Changing variable values must affect actual resources and mission state.

### Mission 03: Traffic Controller

Teach comparison operators, Boolean logic and conditional statements.

Player visits a traffic management center and programs signal behavior.

Traffic lights, waiting vehicles and traffic congestion must respond to the executed solution.

### Mission 04: Construction Automation

Teach for loops and range.

Player controls construction equipment and delivery operations.

The number of repeated operations must correspond to actual loop execution.

### Mission 05: Water Management

Teach while loops.

Player controls water pumps and tank levels using conditions.

Implement visible water levels, pumps, gauges and operational consequences.

### Mission 06: Warehouse Intelligence

Teach lists, dictionaries and indexing.

Player organizes packages, tracks inventory and programs delivery assignments.

Robots or workers must carry out the resulting valid assignments.

### Mission 07: Power Grid

Teach functions, parameters and return values.

Player creates reusable functions to restore electricity in affected buildings.

Correct execution must visibly restore lights and systems.

### Mission 08: Smart Security

Teach string handling, validation and error handling through a fictional access-control system.

Keep the exercise confined to fictional game systems.

### Mission 09: Emergency Routing

Teach algorithms, graphs, BFS and A* pathfinding.

Compare emergency vehicle routes and measure actual simulated journey results.

### Mission 10: Transport Optimization

Teach sorting, searching and data processing.

Improve public transportation schedules and resource allocation.

### Mission 11: Object-Oriented City

Teach classes, objects, attributes and methods.

Allow players to define simulated entities through a controlled Python API.

### Mission 12: City Intelligence

Introduce artificial intelligence through NPC decision-making, basic prediction and optimization.

### Final Academy Mission: City Systems Failure

Combine variables, conditions, loops, functions, data structures and algorithms to restore multiple malfunctioning city systems.

Every mission must include:

- A believable location.
- A cinematic or interactive briefing.
- A clearly defined objective.
- An actual Python coding terminal.
- Optional contextual hints.
- Correct and incorrect code handling.
- Visible physical results.
- Multiple valid solutions where appropriate.
- Mission completion and feedback.
- Saved learning progress.

Provide three assistance levels: Guided, Independent and Challenge.

Use actual Python execution with a restricted simulation interface. Do not execute arbitrary player code inside the main game process.

Run untrusted code through an isolated execution environment with restricted filesystem, process and network access, strict resource limits, execution timeout, validated simulation commands and safe cancellation.

A Python subprocess alone is not a sufficient security sandbox.

Never implement code execution using simple text matching or pretend output.

## 04. Main menu and loading experience

Create a premium original game identity.

The main menu should include:

- Continue Game.
- New Game.
- Living World.
- CodeCity Academy.
- Select Character.
- Player Profiles.
- Settings.
- Credits.
- Exit Game.

Continue must resume the correct save slot and game mode.

Design cinematic loading screens featuring original artwork based on actual game characters, vehicles and city locations.

Include atmospheric sound, smooth transitions, subtle parallax and real loading progress.

Do not add artificial loading delays.

Prepare shaders and heavy assets without blocking the interface unnecessarily.

Provide skip options for previously viewed cinematics.

No generic web-dashboard design, excessive rounded cards, neon gradients, glassmorphism or childish educational styling.

## 05. Player profiles and character selection

Maintain exactly two main playable characters initially:

- Adrian Cole.
- Maya Bennett.

Give both characters unique realistic faces, proportions, hair, clothing, voice characteristics, movement identity and personal backgrounds.

Character selection must contain actual interactive 3D character previews, smooth camera rotation and accurate character information.

Provide multiple local player profiles and save slots.

Each profile should store:

- Player name.
- Selected character.
- Story progression.
- Academy progression.
- Completed missions.
- Achievements.
- Money and inventory.
- Last location.
- Owned vehicles.
- Clothing selections.
- Playtime.
- Gameplay statistics.
- Settings.

Implement manual saves, autosave, checkpoint restoration and corrupted-save recovery.

Use versioned save formats and atomic writes.

## 06. Realistic character production

Continue improving the existing MPFB-based automation.

Do not treat a generic MakeHuman base character as a completed protagonist.

For each playable character, create:

- Distinct facial anatomy.
- Natural body proportions.
- Detailed skin materials.
- Proper eyes, eyebrows, eyelashes and teeth.
- Realistic hair.
- Layered clothing.
- Seams, folds, zippers and stitching.
- Shoes and accessories.
- Complete skeletal rig.
- Finger articulation.
- Facial expression support.
- Animation compatibility.
- Optimized LOD variants.

Create distinct outfits for casual wear, formal wear, outdoor activities and mission-specific appearances.

Reject characters that look like mannequins, dolls, generic low-poly figures or unfinished procedural humans.

Render actual models from front, side, rear and three-quarter angles.

Provide close-up face renders, turntables, clothing inspection and in-engine screenshots.

Test characters under daylight, nighttime and interior lighting.

Provide editable Blender sources and optimized GLB runtime assets.

## 07. NPC population

Create a substantial and varied population rather than repeatedly spawning the same human model.

Initial production targets after vertical-slice approval:

- Two main playable characters.
- At least six named supporting characters.
- At least 24 distinct civilian appearance configurations.
- Additional occupation-specific characters.
- Male and female adults with varied ages, heights and body shapes.
- Elderly characters.
- Police officers.
- Paramedics.
- Firefighters.
- Shopkeepers.
- Office workers.
- Construction workers.
- Taxi drivers.
- Delivery drivers.
- Maintenance workers.
- Restaurant staff.

Use a modular character system to generate additional combinations without unnecessarily increasing memory usage.

Ensure nearby characters do not have visibly duplicated faces, clothes, hairstyles and synchronized movements.

A generated configuration is not equivalent to a separately authored model. Report both quantities honestly.

Target 25 to 40 active nearby NPCs initially, subject to actual performance benchmarks.

Use lightweight background simulation for citizens outside the active area.

## 08. NPC intelligence and independent behavior

The existing Python worker is only a transport probe. Implement a genuine decision-making engine.

NPCs must have individual:

- Personality.
- Goals.
- Memory.
- Needs.
- Occupation.
- Schedule.
- Relationships.
- Environmental awareness.
- Social preferences.
- Emotional state.
- Personal-space boundaries.

Use utility AI, finite state machines, behavior trees and goal-oriented planning where appropriate.

NPCs should continue their daily activities without waiting for player interaction.

Do not make every NPC automatically friendly or helpful.

Different NPCs should react differently to the same situation.

Examples:

- Some acknowledge the player; others ignore them.
- Some complain after being bumped into.
- Some move away from uncomfortable interactions.
- Some react verbally to reckless driving.
- Some recognize the player from earlier encounters.
- Some become impatient while waiting in queues.
- Some continue phone conversations.
- Some change their routes according to weather or congestion.
- Shopkeepers follow operating hours.
- Employees travel between home and work.
- NPCs sit, eat, drink, shop, talk and use their phones.
- Characters respond to interruptions in believable ways.

Implement sight, hearing, line-of-sight checks, personal-space awareness and contextual memory.

Do not display decision trees, emotion bars, NPC intelligence scores or artificial debug indicators during normal gameplay.

The intelligence should be demonstrated through actions and natural reactions.

Integrate Python into the actual gameplay decision pipeline using bounded, asynchronous communication and measured update budgets.

No paid AI API should be required for core gameplay.

## 09. Natural player-to-NPC interactions

Implement contextual interaction when the player approaches another character.

Available actions should depend on distance, orientation, current situation and the NPC's availability.

Support:

- Greet.
- Talk.
- Ask a question.
- Dismiss.
- Wave.
- Joke.
- Apologize.
- Express annoyance.
- Insult.
- Make a rude gesture, including a middle-finger gesture.
- Initiate mission-specific conversations.

Include finger articulation and natural upper-body animation for gestures.

NPCs should notice gestures only when they can reasonably perceive them.

Their response should depend on personality, memory and context.

A rude gesture may result in an annoyed response, reciprocal gesture, dismissal or avoidance rather than the same universal animation.

Provide an optional clean-content setting that disables rude gestures and strong language, especially for Academy Mode and university demonstrations.

Do not interrupt normal gameplay with unnecessary dialogue windows.

Use short contextual interaction prompts.

## 10. Player movement and animation

Build responsive third-person and first-person gameplay.

Implement:

- Walking.
- Jogging.
- Sprinting.
- Jumping.
- Crouching.
- Turning.
- Stair movement.
- Slope handling.
- Sitting.
- Object pickup.
- Carrying items.
- Door interactions.
- Phone usage.
- Vehicle entry and exit.

Use genuine skeletal animations.

Implement locomotion blend spaces, directional movement, foot IK, appropriate hand IK, smooth camera transitions and animation state machines.

Prevent foot sliding, mesh clipping, floating characters, unnatural joints and abrupt animation transitions.

Research and integrate licensed motion-capture animations where permitted.

Do not use simple procedural limb rotation as the final realistic character animation system.

## 11. Controls and input settings

Create fully functional and remappable keyboard, mouse and controller inputs.

Suggested default keyboard controls:

- WASD: Movement and vehicle steering.
- Mouse: Camera control.
- Left Shift: Sprint.
- Space: Jump or vehicle handbrake.
- Left Ctrl: Crouch.
- E: Contextual interaction.
- F: Enter or exit vehicle.
- G: Gesture wheel.
- H: Vehicle horn.
- L: Vehicle lights.
- V: Change camera.
- M: Full map.
- Tab: Inventory or interaction wheel.
- Up Arrow: Smartphone.
- J: Mission journal.
- Escape: Pause menu.

Provide dedicated vehicle acceleration, braking and reverse controls.

Include controller support, adjustable dead zones, vibration strength, mouse sensitivity and inverted camera settings.

Prevent conflicts between driving, walking, menus, code terminals and cutscenes.

When a code editor is focused, gameplay controls must not accidentally activate.

Display controls contextually and provide a complete controls reference in settings.

## 12. Vehicle production

Create genuinely realistic game-ready vehicles.

Initial categories:

- Sports coupe.
- Family sedan.
- Hatchback.
- Executive sedan.
- SUV.
- Pickup truck.
- Motorcycle.
- Taxi.
- Police vehicle.
- Ambulance.
- Fire engine.
- Delivery van.
- City bus.
- Utility truck.

Do not generate one generic mesh and recolor it into every category.

Each vehicle must include realistic:

- Body proportions.
- Wheels and tires.
- Headlights and taillights.
- Indicators.
- Brake lights.
- Mirrors.
- Windows.
- Door handles.
- Panel seams.
- Materials.
- Interior seats.
- Dashboard.
- Steering wheel.
- Instrument cluster.
- Door panels.

Windows must allow appropriate visibility into modeled vehicle interiors.

Doors, wheels and steering must use correct pivots.

Player characters and NPCs must sit correctly inside vehicles with believable hand positions and entry/exit animations.

Implement first-person cockpit and third-person driving views.

Use original vehicle designs and fictional branding.

## 13. Driving physics

Evaluate the existing researched open-source vehicle systems.

Implement:

- Acceleration.
- Braking.
- Reverse.
- Steering.
- Handbrake.
- Suspension.
- Tire grip.
- Weight transfer.
- Vehicle-specific handling.
- Collisions.
- Surface-dependent traction.
- Rain-related grip changes.
- Engine behavior.
- Gear changes.

Cars should not feel like floating objects sliding over roads.

Implement appropriate differences between sports cars, trucks, buses and ordinary civilian vehicles.

Use performance-conscious raycast suspension or another tested vehicle architecture.

Evaluate physics accuracy and CPU cost before increasing simulation tick rates.

## 14. City map and environment

Build an original modern coastal city with recognizable locations and geographically believable road connections.

Develop Harbor Boulevard as the first detailed vertical slice.

After approval, expand into:

- Downtown.
- Residential district.
- Commercial district.
- Industrial district.
- Waterfront.
- University and technology campus.
- Public parks.
- Transport hubs.

Create a coherent city rather than randomly scattered buildings.

Include roads, alleys, sidewalks, pedestrian crossings, parking spaces, bridges, traffic lights, street signs, bus stops, trees, benches, utility poles, construction sites and environmental details.

Use varied architecture and realistic building dimensions.

All playable areas must have valid collision and navigation.

Provide visible landmarks and meaningful locations for story and Academy missions.

Initial post-slice production targets may include 50 to 80 visually distinct building configurations and at least eight functional interiors. Expand only after profiling and visual acceptance.

## 15. Functional interiors

Create actual enterable buildings rather than decorative doors.

Priority locations:

- Player apartment.
- Convenience store.
- Coffee shop.
- Restaurant.
- Police station.
- Vehicle garage.
- Hospital reception.
- Technology campus.
- Control room.
- Warehouse.
- Power station.
- Traffic management center.

Include believable furniture, equipment, lighting, doors, windows, floors, ceilings and contextual objects.

Ensure buildings have exterior geometry and appropriate interior transitions.

Use interior streaming or occlusion systems where required.

NPCs must navigate and perform activities inside supported interiors.

## 16. Minimap and full map

Implement a real map generated from actual city geometry and navigation data.

The minimap should show:

- Player position.
- Heading.
- Roads.
- Nearby relevant locations.
- Mission destinations.
- Waypoints.
- Appropriate nearby icons.

The full map must support zooming, panning, location selection, waypoint placement and route calculation.

Route guidance must follow actual roads or pedestrian paths.

Do not use decorative static map screenshots disconnected from the playable world.

Keep HUD minimal and visually coherent.

## 17. Traffic and pedestrian simulation

Implement connected road lanes and intersections.

Traffic vehicles must:

- Follow valid routes.
- Stop at red lights.
- Maintain reasonable following distances.
- Yield appropriately.
- Navigate turns.
- Park where supported.
- Respond to obstacles.
- Avoid unnecessary collisions.
- Recover from blocked routes.

Pedestrians should use sidewalks, crossings and destinations.

Implement vehicle and pedestrian spawning outside direct player view where possible.

Avoid obvious pop-in and repetitive traffic loops.

Use pooled entities, efficient spatial indexing and distance-based simulation.

## 18. Story missions and world activities

Develop an interconnected storyline for Living World.

Suggested chapters:

1. A New Beginning.
2. The Missing Person.
3. The Blackout.
4. Undercover.
5. The Pursuit.
6. The Final Decision.

Provide realistic mission objectives and consequences rather than repetitive marker collection.

Include exploration, investigation, conversations, driving, environmental interactions and alternative decisions.

Add optional activities such as taxi jobs, delivery assignments, vehicle maintenance, shopping, photography and city exploration.

Support checkpoint retry, mission cancellation where appropriate, mission replay and clear objective tracking.

Do not force educational content into Living World missions.

## 19. Smartphone and inventory

Create an actual in-game smartphone interface.

Include working applications for:

- Messages.
- Contacts.
- Calls.
- Maps.
- Missions.
- Camera.
- Weather.
- Banking.
- Taxi services.
- City news.

Only display applications that have functional implementations.

Messages and news should react to supported story and world events.

Add a functional inventory system with appropriate items, keys, equipment and mission objects.

Do not create decorative nonfunctional buttons.

## 20. World time and weather

Implement continuous world time with morning, afternoon, evening and nighttime.

Include:

- Dynamic sun and moon lighting.
- Streetlights.
- Building illumination.
- Shop schedules.
- Traffic density changes.
- NPC routine changes.
- Clear weather.
- Cloudy weather.
- Rain.
- Fog where appropriate.

Weather must affect gameplay and NPC behavior.

Include umbrellas, reduced vehicle traction and contextual changes in outdoor activities.

Avoid expensive effects that compromise ordinary laptop performance.

## 21. Visual effects

Implement polished real-time VFX.

Required examples:

- Tire dust and water spray.
- Brake lights and light emission.
- Vehicle exhaust.
- Rain particles.
- Puddles and wet road materials.
- Footstep dust where appropriate.
- Electrical sparks for relevant missions.
- Steam.
- Smoke.
- Water movement.
- Environmental wind.
- Weather-dependent effects.

Use decals, particles, shaders and optimized materials appropriately.

Support graphics-quality settings for reflections, particles, shadows, volumetric effects and post-processing.

Do not cover poor asset quality with excessive bloom, fog or motion blur.

## 22. Sound design

Audio must be treated as a major production system.

Create or source properly licensed sounds for:

- Walking and running on different surfaces.
- Character movement.
- Vehicle engine idle and acceleration.
- Gear changes.
- Braking.
- Tire skid.
- Horns.
- Door opening and closing.
- Rain.
- Wind.
- Distant traffic.
- City ambience.
- Shop ambience.
- Emergency sirens.
- Phone notifications.
- Menu interactions.
- Mission success and failure.
- Environmental equipment.
- Construction operations.
- Water pumps and power equipment.

Use spatial 3D audio and appropriate distance attenuation.

Engine pitch must respond to engine state.

Footsteps must synchronize with actual animation.

Use audio variation to prevent repetitive identical sounds.

Provide original or properly licensed background music and cinematic audio.

Do not copy copyrighted GTA music or audio files.

## 23. Dialogue and voice

Provide contextual NPC dialogue and reactions.

Use concise, natural speech.

Avoid robotic repetitive exposition.

Academy guidance may use a friendly voice that explains only relevant concepts and responds to the player's current mission.

Include subtitles and narration speed controls at 1x, 1.5x and 2x where supported.

Do not read every interface label aloud.

Support dialogue skipping and subtitle-only mode.

Core gameplay must remain playable without network access or paid text-to-speech services.

## 24. Pause menu and complete settings

The pause menu must actually pause applicable gameplay systems.

Include:

- Resume.
- Map.
- Missions.
- Player profile.
- Save game.
- Load game.
- Settings.
- Restart checkpoint.
- Return to main menu.
- Quit.

Settings must include functional controls for:

### Graphics
Resolution, fullscreen/windowed mode, VSync, FPS limit, resolution scale, texture quality, shadow quality, anti-aliasing, reflections, draw distance, NPC density, traffic density, particles, weather effects and motion blur.

### Audio
Master volume, music volume, effects volume, dialogue volume, vehicle volume, environmental volume and mute options.

### Gameplay
Camera preference, difficulty, contextual hints, subtitles, camera shake, clean-content mode and interaction preferences.

### Controls
Keyboard and controller remapping, mouse sensitivity, camera inversion, controller dead zones and vibration.

### Accessibility
Text size, subtitle background, reduced motion, reduced flashing and readable interaction prompts.

Every setting must have a real measurable or visible effect and persist across restarts.

## 25. Improve the existing asset automation

Extend the current Poly Haven and MPFB automation into a complete asset production pipeline.

The pipeline should support:

1. Licensed asset discovery.
2. Source download.
3. License verification.
4. Hash verification.
5. Blender import.
6. Material reconstruction.
7. Scale correction.
8. UV validation.
9. Mesh optimization.
10. LOD generation.
11. Collision generation.
12. Rigging where appropriate.
13. GLB export.
14. Multi-angle rendering.
15. Godot import.
16. In-engine visual inspection.
17. Performance validation.
18. Registry approval.

Create independent pipelines for characters, vehicles, buildings, interiors, props and environmental objects.

Use licensed professional meshes wherever practical.

Do not attempt to generate realistic human models or complex vehicles exclusively from primitive geometry.

Preserve editable sources.

Improve script reliability, rerun behavior, dependency caching, failure recovery and output provenance.

Do not claim a candidate is complete merely because Blender rendered it.

Every approved asset must pass actual visual and gameplay inspection.

## 26. AI-assisted asset creation

Investigate free and open-weight image-to-3D or text-to-3D approaches where hardware and licenses permit.

Potential candidates for evaluation include TripoSR, Hunyuan3D, TRELLIS and Stable Fast 3D.

These are research candidates, not preapproved dependencies.

Verify current licenses, model-weight terms, hardware requirements, setup costs and output quality before adoption.

Use AI-generated 3D assets primarily for suitable props and environment objects.

Do not automatically trust generated topology, UVs, materials, rigging or scale.

Repair and optimize generated meshes in Blender.

Reject defective or visually inconsistent assets.

If local hardware cannot support a model, prioritize professionally licensed downloadable assets rather than relying on paid generation services or pretending generation succeeded.

## 27. Actual open-source integration

The existing source audit is useful, but source research alone is insufficient.

Inspect and isolate the pinned candidate repositories already listed in THIRD_PARTY_NOTICES.md.

Evaluate:

- OpenCity for open-world gameplay patterns, traffic and vehicle interaction.
- GDQuest for compatible third-person controller code.
- Official Godot demos for physics, navigation, animation and interaction patterns.
- Easy Vehicle Physics for driving systems.
- Godot Road Generator for road network authoring.
- MPFB2 for human asset generation.
- Poly Haven for realistic licensed models, materials and lighting.
- ambientCG for PBR materials.
- Mixamo for individually reviewed animation use.
- Other suitable licensed sound and asset libraries.

Find additional open-source alternatives where existing candidates fail.

Verify exact source revisions and individual asset licenses.

Test each candidate in an isolated environment.

Extract or adapt only compatible and useful modules.

Do not import an entire unrelated demo game and inherit its visual style.

Preserve copyright notices and required attribution.

Do not distribute noncommercial, proprietary, leaked or ripped assets without appropriate permission.

Update the source ledger with actual integration status, exact files reused, modifications, tests and measured performance.

## 28. Performance engineering

The game must not become a laggy city simulation.

Maintain a performance-first architecture.

Implement:

- Chunk-based streaming.
- Asynchronous loading.
- Frustum culling.
- Occlusion culling where appropriate.
- Mesh LOD.
- Animation LOD.
- NPC intelligence LOD.
- Traffic pooling.
- Shared materials.
- Texture compression.
- GPU instancing.
- Efficient navigation.
- Efficient collision.
- Distance-based sound processing.
- Bounded Python communication.
- Memory management.

Target a stable 30 FPS at 720p on a specified low-end reference laptop and 60 FPS at 1080p on an appropriately capable dedicated GPU.

These are engineering targets, not guaranteed results.

Measure frame times, 1% lows, RAM, VRAM, loading duration and stutter.

Profile crowded intersections, rain, nighttime, high-speed driving and interiors.

Do not hide performance problems by reducing all characters to primitive objects.

Offer suitable graphics presets and scalable population density.

## 29. Automation and local verification

Maintain GitHub-based development.

Do not rely exclusively on GitHub Actions availability.

Provide equivalent local PowerShell and Python verification commands for asset generation, source validation, tests, Godot import, smoke testing and Windows export.

Cache reusable toolchains and approved source downloads.

Avoid duplicate large downloads.

Never commit temporary assets, build caches, credentials or uncontrolled generated binaries.

Check storage and Git LFS limits before tracking large assets.

Provide reproducible manifests for required game assets.

Ensure the final Windows build can run offline without requiring the user to install Blender, Godot or a separate development environment.

Package required permitted runtime components.

## 30. Code health and reliability

Perform continuous code health audits.

Check for:

- Duplicate implementations.
- Unused code.
- Broken imports.
- Missing dependencies.
- Invalid references.
- Unsafe filesystem access.
- Memory leaks.
- Unbounded loops.
- Excessive per-frame allocations.
- Blocking processes.
- Race conditions.
- Save corruption.
- Broken scene transitions.
- Invalid navigation paths.
- Collision defects.
- Animation state errors.
- Input conflicts.
- Broken UI controls.

Add targeted automated regression tests.

Do not disable meaningful validation to make tests appear successful.

Fix root causes rather than hiding failures.

## 31. Required documentation

Maintain and update:

- AGENTS.md
- ARCHITECTURE.md
- ROADMAP.md
- FILEMAP.md
- HISTORY.md
- README.md
- ASSET_REGISTRY.md
- PERFORMANCE.md
- THIRD_PARTY_NOTICES.md
- docs/ASSET_PIPELINE.md
- docs/QA.md
- docs/ACADEMY_CURRICULUM.md
- docs/NPC_INTELLIGENCE.md
- docs/GAMEPLAY_SYSTEMS.md
- docs/AUDIO_VFX.md
- docs/CONTROLS.md
- docs/RENDER_REVIEW.md

Avoid unnecessary duplicate documentation.

Document actual implementation status separately from planned features.

## 32. Immediate next-phase instructions

Continue from the latest completed Phase A checkpoint.

First:

- Finish outstanding foundation verification.
- Inspect actual character candidate outputs.
- Resolve MPFB rendering and dependency issues.
- Improve Adrian and Maya candidates independently.
- Produce one realistic sports coupe candidate with actual interior.
- Produce the first high-quality street segment.
- Test relevant open-source player and vehicle systems.
- Update the architecture for Living World and Academy modes.
- Establish a shared world-interaction API.
- Prepare real profile, mode-selection and loading-screen architecture.

Then build the first complete vertical slice containing:

- One detailed explorable street.
- Two selectable playable characters.
- At least six independently behaving NPCs.
- One fully driveable realistic vehicle.
- One functional interior.
- Real minimap and full map.
- One Living World mission.
- One fully functional Academy programming mission.
- Natural NPC dialogue and gestures.
- Working pause menu and settings.
- Appropriate sound effects.
- Saved progress.

Do not mark incomplete features as finished.

Do not expand the entire city before the vertical slice is visually inspected, interactively tested and performance-profiled.

## 33. Evidence required after every phase

Report:

1. Exact changes implemented.
2. Actual assets generated and their counts.
3. Approved assets versus unapproved candidates.
4. Third-party source modules integrated.
5. Real screenshots of the actual game.
6. Character front, side, rear and close-up renders.
7. Vehicle exterior and interior renders.
8. Gameplay evidence.
9. Test commands and actual outputs.
10. Performance measurements and test hardware.
11. Known defects and limitations.
12. Pending acceptance gates.
13. Next development priorities.
14. Commit and pull request status.

Visual evidence must come from actual generated models or the running game, not AI concept images presented as implemented assets.

Continue implementation in focused, testable phases. Keep the repository clean and maintainable. Deliver genuine gameplay, realistic visual assets, strong artificial intelligence and a polished educational experience.
