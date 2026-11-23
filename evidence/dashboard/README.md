# Dashboard evidence

Captured Nov 2026 on dashboard.fortyguard.com with an intern-session trial account
(subscribed state: Indiana). No keys or emails appear in these files.

| File | Shows |
|---|---|
| 01_toast_stack_desktop.png | One "Polygon is outside your Subscribed State" toast per rejected edit; they stack down past the viewport and cover the map |
| 02_toast_stack_mobile.png | Same stack on a phone-width screen, hiding most of the map |
| 03_polygon_crossing_state_border.png | Polygon being drawn inside Indiana toward the Ohio line (213.80 km² so far); the point on the state line triggers the out-of-state warning |
| 04_upload_jpeg_misleading_message.png | A .jpeg is selected in Upload Polygon, yet the tooltip says "Choose a file before confirming" |
| 05_generate_enabled_without_shape.png | Area 0 km² and no shape, but Generate Map is enabled; Task Progress says "No task generation in progress" |
| 06_generation_failed_toasts.png | The resulting generic "Heatmap generation failed. Please try again later." toasts, with no reason given |
| 07_chatbot_state_change_unclear.png | Assistant first implies the subscribed state is fixed, then admits it does not know the policy |
| 08_chatbot_cannot_change_from_dashboard.png | Assistant says the state cannot be changed from the dashboard; nothing in the UI says this |
| 09_time_picker_no_timezone.png | Time picker offers hours only, with no timezone selector |
| 10_mobile_map_comparison_no_scroll.mp4 | Map Comparison page at phone width (9 s); a 1-finger drag on the map shows "Use two fingers to move the map" and the page does not scroll |
| 11_welcome_card_worldwide.png | Welcome card: "Explore temperature conditions for any location worldwide" |
| 12_profile_us_states_only.png | Profile step: "U.S. states only" badge and a required "Access US State" field (contradicts the welcome card) |
| 13_size_limit_warning_during_drag.png | Dragging a shape from outside the subscribed state to inside: "Maximum Polygon Size Limit (388.50 Km²)" warnings stack up while the panel reads 275.29 km² |
| 14_size_limit_warning_drag.mp4 | 8 s recording of the same drag |
| 15_devtools_toast_container.png | DevTools: the whole toast stack is one 320 x 960 px `p-toast` element over the map |
| 16_upload_no_network_request.png | .jpeg selected, Confirm clicked, Network tab shows no upload request |
| 17_tour_steps_3_to_8.png | Interactive tour steps 3 to 8 side by side |
