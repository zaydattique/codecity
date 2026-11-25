extends RefCounted
## Shared CodeCity interface theme. One palette, real readable controls.
static func panel(color: Color=Color(0.035,0.055,0.075,0.98), radius: int=8, margin: int=20) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color=color
	style.border_color=Color(0.20,0.29,0.34)
	style.set_border_width_all(1)
	style.set_corner_radius_all(radius)
	style.content_margin_left=margin
	style.content_margin_right=margin
	style.content_margin_top=margin
	style.content_margin_bottom=margin
	return style

static func theme() -> Theme:
	var t := Theme.new()
	t.default_font_size=17
	var text := Color(0.89,0.92,0.94)
	t.set_color("font_color","Label",text)
	for kind: String in ["Button","OptionButton","CheckButton"]:
		t.set_color("font_color",kind,text)
		t.set_color("font_hover_color",kind,Color.WHITE)
		t.set_color("font_pressed_color",kind,Color.WHITE)
		t.set_stylebox("normal",kind,panel(Color(0.10,0.15,0.18),5,10))
		t.set_stylebox("hover",kind,panel(Color(0.16,0.23,0.27),5,10))
		t.set_stylebox("pressed",kind,panel(Color(0.12,0.38,0.43),5,10))
		t.set_stylebox("disabled",kind,panel(Color(0.07,0.09,0.11),5,10))
		t.set_stylebox("focus",kind,panel(Color(0.1,0.22,0.27,0.3),5,0))
	t.set_stylebox("panel","PanelContainer",panel())
	t.set_stylebox("normal","LineEdit",panel(Color(0.07,0.10,0.12),5,10))
	t.set_color("font_color","LineEdit",text)
	t.set_color("font_placeholder_color","LineEdit",Color(0.55,0.63,0.69))
	t.set_stylebox("normal","CodeEdit",panel(Color(0.055,0.075,0.095),5,12))
	t.set_color("font_color","CodeEdit",text)
	t.set_color("font_color","TextEdit",text)
	t.set_color("background_color","CodeEdit",Color(0.055,0.075,0.095))
	t.set_color("caret_color","CodeEdit",Color(0.55,0.91,0.95))
	return t
