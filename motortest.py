
import time
import lgpio


# TB6612FNG #1 - 왼쪽 바퀴
LEFT_FRONT_PWM = 12
LEFT_FRONT_IN1 = 5
LEFT_FRONT_IN2 = 6

LEFT_REAR_PWM = 13
LEFT_REAR_IN1 = 16
LEFT_REAR_IN2 = 20

# TB6612FNG #2 - 오른쪽 바퀴
RIGHT_FRONT_PWM = 18
RIGHT_FRONT_IN1 = 23
RIGHT_FRONT_IN2 = 24

RIGHT_REAR_PWM = 19
RIGHT_REAR_IN1 = 26
RIGHT_REAR_IN2 = 21

# STBY 핀
STBY_1 = 25   # 모터드라이버 1번 STBY
STBY_2 = 17   # 모터드라이버 2번 STBY

# PWM 설정
PWM_FREQ = 1000
TEST_SPEED = 40   # 처음 테스트는 30~50 추천


# =========================
# 모터 정보 묶기
# =========================

MOTORS = {
    "왼쪽 앞바퀴": {
        "pwm": LEFT_FRONT_PWM,
        "in1": LEFT_FRONT_IN1,
        "in2": LEFT_FRONT_IN2
    },
    "왼쪽 뒷바퀴": {
        "pwm": LEFT_REAR_PWM,
        "in1": LEFT_REAR_IN1,
        "in2": LEFT_REAR_IN2
    },
    "오른쪽 앞바퀴": {
        "pwm": RIGHT_FRONT_PWM,
        "in1": RIGHT_FRONT_IN1,
        "in2": RIGHT_FRONT_IN2
    },
    "오른쪽 뒷바퀴": {
        "pwm": RIGHT_REAR_PWM,
        "in1": RIGHT_REAR_IN1,
        "in2": RIGHT_REAR_IN2
    }
}


# =========================
# GPIO 초기화
# =========================

h = lgpio.gpiochip_open(0)

ALL_PINS = [
    LEFT_FRONT_PWM, LEFT_FRONT_IN1, LEFT_FRONT_IN2,
    LEFT_REAR_PWM, LEFT_REAR_IN1, LEFT_REAR_IN2,
    RIGHT_FRONT_PWM, RIGHT_FRONT_IN1, RIGHT_FRONT_IN2,
    RIGHT_REAR_PWM, RIGHT_REAR_IN1, RIGHT_REAR_IN2,
    STBY_1, STBY_2
]

for pin in ALL_PINS:
    lgpio.gpio_claim_output(h, pin)


# =========================
# 제어 함수
# =========================

def enable_drivers():
    lgpio.gpio_write(h, STBY_1, 1)
    lgpio.gpio_write(h, STBY_2, 1)


def disable_drivers():
    lgpio.gpio_write(h, STBY_1, 0)
    lgpio.gpio_write(h, STBY_2, 0)


def motor_forward(motor, speed):
    pwm = motor["pwm"]
    in1 = motor["in1"]
    in2 = motor["in2"]

    lgpio.gpio_write(h, in1, 1)
    lgpio.gpio_write(h, in2, 0)
    lgpio.tx_pwm(h, pwm, PWM_FREQ, speed)


def motor_backward(motor, speed):
    pwm = motor["pwm"]
    in1 = motor["in1"]
    in2 = motor["in2"]

    lgpio.gpio_write(h, in1, 0)
    lgpio.gpio_write(h, in2, 1)
    lgpio.tx_pwm(h, pwm, PWM_FREQ, speed)


def motor_stop(motor):
    pwm = motor["pwm"]
    in1 = motor["in1"]
    in2 = motor["in2"]

    lgpio.tx_pwm(h, pwm, PWM_FREQ, 0)
    lgpio.gpio_write(h, in1, 0)
    lgpio.gpio_write(h, in2, 0)


def stop_all():
    for motor in MOTORS.values():
        motor_stop(motor)


def cleanup():
    print("\n모터 정지 중...")
    stop_all()
    time.sleep(0.2)

    print("모터드라이버 비활성화")
    disable_drivers()
    time.sleep(0.2)

    lgpio.gpiochip_close(h)
    print("GPIO 정리 완료")


def test_motor(name, motor):
    print(f"\n[{name}] 전진 테스트")
    motor_forward(motor, TEST_SPEED)
    time.sleep(2)

    print(f"[{name}] 정지")
    motor_stop(motor)
    time.sleep(1)

    print(f"[{name}] 후진 테스트")
    motor_backward(motor, TEST_SPEED)
    time.sleep(2)

    print(f"[{name}] 정지")
    motor_stop(motor)
    time.sleep(1)


# =========================
# 메인 실행
# =========================

try:
    print("모터드라이버 활성화")
    enable_drivers()
    time.sleep(1)

    for name, motor in MOTORS.items():
        test_motor(name, motor)

    print("\n전체 모터 테스트 완료")

except KeyboardInterrupt:
    print("\nCtrl + C 감지됨")

except Exception as e:
    print("\n오류 발생:", e)

finally:
    cleanup()