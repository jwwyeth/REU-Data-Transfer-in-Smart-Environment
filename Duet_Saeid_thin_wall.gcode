;(Duet_thin_wall) 
;(Written by Freddy 2024-05-28 14:16:26.189032) 
;(Remember to use G10 L20 P* to setup system's origin) 
 
; M42 P1 S* : Laser Modulation; 0~1 
; M42 P2 S* : Feeder_ Analog On/Off; 0~1 
; M42 P3 S* : Feeder_ Digital On/Off; 0 or 1 


; setup process parameters
var LP_pre = 0.5 * 255
var LP = 0.45 * 255
var FR = 0.168  ;  ??g/min; Need to make powder calibration
var SS = 800  ; mm/min
var Z_inc = 0.35 ; mm
var Dwell = 150 ; 150 ms 

; setup geometrical variables
var length = 41      ; Set the length
var x_offset = 7 ; Set the X offset
var y_offset = 6.35 ; Set the Y offset

; Layers setup
var pre_layers = 4
var main_layers = 6



M98 P"/Macros/Motion_Test/G55_Origin"
G21 G90 G17 G55 ;(mm, ABS, xy plane, g55 system) 

G4 S2(Wait for 2 seconds)
G1 X{var.x_offset} Y{var.y_offset} F800
G4 S2 (Wait for 2 seconds)
G91


M42 P1 S1 ; Laser On: Modulation Signal
;---Preheating
var iterations_1 = 0 ; Initialize the loop counter
while var.iterations_1 < 1
	G1 X{var.length} F1000 S{var.LP_pre}
	G1 X{-var.length} F1000 S{var.LP_pre}

	; Increment the loop counter
  	set var.iterations_1 = var.iterations_1 + 1
G4 P1
echo "CHECK POINT1"



;-----Open feeder and wait 2 sec
M42 P3 S1 ; Powder Feeder On: Digital Signal
M42 P2 S{var.FR} ; Powder Feeder Rate: Analog Signal. Need to measure the feedrate
G4 P2000 ; Wait 2000 ms

;----Initial Deposit
var iterations_2 = 0
while var.iterations_2 < {var.pre_layers}*0.5
	G1 X{var.length} F{var.SS} S{var.LP_pre}
	G1 Z{var.Z_inc} F200
	G1 X{-var.length} F{var.SS} S{var.LP_pre}
	G1 Z{var.Z_inc} F200
	set var.iterations_2 = var.iterations_2 + 1
G4 P1
echo "Check point2"


;----Main Deposit
var iterations_3 = 0
while var.iterations_3 < {var.main_layers}*0.5
	G1 X{var.length} F{var.SS} S{var.LP}
	G1 Z{var.Z_inc} F200
	G1 X{-var.length} F{var.SS} S{var.LP}
	G1 Z{var.Z_inc} F200
	set var.iterations_3 = var.iterations_3 + 1




; End. Turn off everything
M42 P1 S0 ; Disable pwm laser signal 
M42 P2 S0 ; Disable Powder feeder's analog signal 
M42 P3 S0 ; Disable Powder feeder's digital signal 

G4 P1
echo "Deposit is done"
; Today is finished













