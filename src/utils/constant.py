#PWM Signal is between 1000us (0%) and 2000us (100%) 
pwm_low_us = 1000 # signal duration of pwm for 0% power
pwm_high_us = 2000 # signal duration of pwm for 100% power
pwm_frequency = 50 # Frequency of PWM signal sent
pwm_low_ratio = (pwm_low_us/((1/pwm_frequency)*1000000)) #Percentage for 0% power motor
pwm_high_ratio = (pwm_high_us/((1/pwm_frequency)*1000000)) #Percentage for 100% power motor
pwm_low = pwm_low_ratio * 65535
pwm_high = pwm_high_ratio * 65535