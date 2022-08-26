from pygame import mixer


mixer.init()

circles = mixer.Sound("audio/circles.ogg")
welcome = mixer.Sound("audio/welcome.mp3")
seeya = mixer.Sound("audio/seeya.mp3")

confirm = mixer.Sound("audio/confirm-selection.wav")
button = mixer.Sound("audio/button-select.wav")
select = mixer.Sound("audio/ruleset-select-osu.wav")

pausing = mixer.Sound("audio/pause-loop.mp3")
miss = mixer.Sound("audio/combobreak.mp3")
applause = mixer.Sound("audio/applause-a.wav")
