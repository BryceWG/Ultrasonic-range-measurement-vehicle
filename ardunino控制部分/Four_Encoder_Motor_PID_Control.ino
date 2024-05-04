#include <MsTimer2.h> // 引入MsTimer2库，用于设置定时中断
#include <Arduino.h> // 引入Arduino标准库，用于Arduino的基本操作
// 定义电机编码器的引脚，用于测量转速
#define M1_ENCODER_A 2 // 右前电机编码器A相引脚，用于下降沿捕获
#define M1_ENCODER_B 40 // 右前电机编码器B相引脚

#define M2_ENCODER_A 3 // 左前电机编码器A相引脚，用于下降沿捕获
#define M2_ENCODER_B 41 // 左前电机编码器B相引脚

#define M3_ENCODER_A 20 // 左后电机编码器A相引脚，用于下降沿捕获
#define M3_ENCODER_B 42 // 左后电机编码器B相引脚

#define M4_ENCODER_A 21 // 右后电机编码器A相引脚，用于下降沿捕获
#define M4_ENCODER_B 43 // 右后电机编码器B相引脚

// 定义电机驱动TB6612的控制引脚
#define TB6612_M1_IN1 22
#define TB6612_M1_IN2 23
#define Motor_M1_PWM 4 // 右前电机PWM控制引脚

#define TB6612_M2_IN1 24
#define TB6612_M2_IN2 25
#define Motor_M2_PWM 5 // 左前电机PWM控制引脚

#define TB6612_M3_IN1 26
#define TB6612_M3_IN2 27
#define Motor_M3_PWM 6 // 左后电机PWM控制引脚

#define TB6612_M4_IN1 28
#define TB6612_M4_IN2 29
#define Motor_M4_PWM 7 // 右后电机PWM控制引脚

typedef struct
{
    float input;      // PID输入值（目标速度）
    float output;     // PID输出值（调整后的PWM值）
    float feedback;   // PID反馈值（实际速度）
    float k_p;        // 比例系数
    float k_i;        // 积分系数
    float k_d;        // 微分系数
    float err_1;      // 前一次误差
    float err_2;      // 前两次误差
    float err_x;      // 累计误差

    float out_max;    // 输出最大值
    float out_min;    // 输出最小值
    float err_x_max;  // 累计误差最大值
} PID;

// 定义中断变量，用于计数脉冲
volatile float motor_M1 = 0; 
volatile float motor_M2 = 0; 
volatile float motor_M3 = 0;
volatile float motor_M4 = 0;

int timecnt = 0; // 50ms计时器
int time_seconds = 0; // 秒计时器
float V_M1 = 0; // 临时存储右前电机速度变量
float V_M2 = 0; // 临时存储左前电机速度变量
float V_M3 = 0; // 临时存储左后电机速度变量
float V_M4 = 0; // 临时存储右后电机速度变量
int motor_M1_dir = 0; // 反馈的右前电机转动方向
int motor_M2_dir = 0; // 反馈的左前电机转动方向
int motor_M3_dir = 0; // 反馈的左后电机转动方向
int motor_M4_dir = 0; // 反馈的右后电机转动方向
int angle = 0; // 小车当前旋转角度
PID M1_Motor_PID, M2_Motor_PID, M3_Motor_PID, M4_Motor_PID; // PID结构体实例

// 函数声明
void Motor_PWM_Set(float M1_PWM, float M2_PWM, float M3_PWM, float M4_PWM);// 设置电机PWM值以控制速度和方向
void Motor_Init(void);// 初始化电机控制引脚
void PID_Init(void);// 初始化PID控制器参数
void PID_Cal(PID *pid);// 计算PID控制器的输出
void Read_Motor(void);
void Read_Motor_V(void);// 读取电机速度（通过编码器脉冲）
void PID_Cal_Computer_Out(void);// 定期计算PID输出并更新电机PWM值
void Motor_Test(void);// 电机测试函数，用于验证电机运行
void turnleft90(void);

void setup()// Arduino的setup函数，用于初始化
{
    Motor_Init();                    //电机端口初始化
    PID_Init();
    MsTimer2::set(50, PID_Cal_Computer_Out); // 50ms period
    MsTimer2::start();
    Serial.begin(9600);              //打开串口
}

//主循环
void loop()
{
    turnleft90();
    Read_Motor_V(); // 读取并计算电机速度
    // 串口输出电机的目标速度和实际反馈速度，用于调试
    Serial.print(M1_Motor_PID.input);
    Serial.print(",");
    Serial.print(M1_Motor_PID.feedback);
    Serial.print(",");
    Serial.print(M2_Motor_PID.input);
    Serial.print(",");
    Serial.print(M2_Motor_PID.feedback);
    Serial.print(",");
    Serial.print(M3_Motor_PID.input);
    Serial.print(",");
    Serial.print(M3_Motor_PID.feedback);
    Serial.print(",");
    Serial.print(M4_Motor_PID.input);
    Serial.print(",");
    Serial.println(M4_Motor_PID.feedback);
}

// 电机测试函数，逐步改变电机的目标速度，用于测试和调试
void moveforward50(void) 
{
    if(time_seconds< 1)
    {
        M1_Motor_PID.input = 0;
        M2_Motor_PID.input = 0;
        M3_Motor_PID.input = 0;
        M4_Motor_PID.input = 0;
    }
    if(time_seconds >= 1 && time_seconds < 5)
    {
        M1_Motor_PID.input = 200;
        M2_Motor_PID.input = 200;
        M3_Motor_PID.input = 200;
        M4_Motor_PID.input = 200;
    }
    if(time_seconds >= 5)
    {
        M1_Motor_PID.input = 0;
        M2_Motor_PID.input = 0;
        M3_Motor_PID.input = 0;
        M4_Motor_PID.input = 0;
    }
}
void turnleft90(void)
{
    M1_Motor_PID.input = 267;
    M2_Motor_PID.input = -267;
    M3_Motor_PID.input = -267;
    M4_Motor_PID.input = 267;
    if(angle >= 90)
    {
        M1_Motor_PID.input = 0;
        M2_Motor_PID.input = 0;
        M3_Motor_PID.input = 0;
        M4_Motor_PID.input = 0;
    }
}

// 定期计算PID输出并更新电机PWM值，由定时器调用
/**
 * PID计算及电机输出调整函数
 * 本函数周期性地调用PID计算函数以更新对四个电机的控制输出，并根据计算结果设置电机的PWM信号，从而控制电机的速度和方向。
 * 此外，函数还负责更新时间计数器，用以控制测试流程的进度和PID计算的频率。
 * 
 * 参数: 无
 * 返回值: 无
 */
void PID_Cal_Computer_Out(void)
{
    // 对四个电机的PID控制器进行计算
    PID_Cal(&M1_Motor_PID);
    PID_Cal(&M2_Motor_PID);
    PID_Cal(&M3_Motor_PID);
    PID_Cal(&M4_Motor_PID);
    
    // 根据PID计算结果，设置四个电机的PWM输出，以控制电机转速和方向
    Motor_PWM_Set(M1_Motor_PID.output, M2_Motor_PID.output, M3_Motor_PID.output, M4_Motor_PID.output);
    
    timecnt++;// 更新时间计数器，用于控制测试流程和PID计算频率
    
    // 每20次循环增加一秒计时，并重置时间计数器
    if(timecnt == 20)
    {
        time_seconds++;
        timecnt = 0;
    }
}

/**
设置PWM控制电机的正反转和占空比
 * @param M1_PWM 控制电机1的PWM值，正数表示正转，负数表示反转
 * @param M2_PWM 控制电机2的PWM值，正数表示正转，负数表示反转
 * @param M3_PWM 控制电机3的PWM值，正数表示正转，负数表示反转
 * @param M4_PWM 控制电机4的PWM值，正数表示正转，负数表示反转
 * HIGH LOW（1 0）表示反转
 * 该函数根据传入的PWM值设置对应电机的转动方向和PWM占空比，实现电机的控制。
 */
void Motor_PWM_Set(float M1_PWM, float M2_PWM, float M3_PWM, float M4_PWM)
{

    // 设置电机1的正反转及PWM值
    if(M1_PWM > 0)
    {
        digitalWrite(TB6612_M1_IN1, HIGH);
        digitalWrite(TB6612_M1_IN2, LOW);
        analogWrite(Motor_M1_PWM, M1_PWM);
    }
    else
    {
        digitalWrite(TB6612_M1_IN1, LOW);
        digitalWrite(TB6612_M1_IN2, HIGH);
        analogWrite(Motor_M1_PWM, -1 * M1_PWM);
    }

    // 设置电机2的正反转及PWM值
    if(M2_PWM > 0)
    {
        digitalWrite(TB6612_M2_IN1, LOW);
        digitalWrite(TB6612_M2_IN2, HIGH);
        analogWrite(Motor_M2_PWM, M2_PWM);
    }
    else
    {
        digitalWrite(TB6612_M2_IN1, HIGH);
        digitalWrite(TB6612_M2_IN2, LOW);
        analogWrite(Motor_M2_PWM, -1 * M2_PWM);
    }

    // 设置电机3的正反转及PWM值
    if(M3_PWM > 0) {
        digitalWrite(TB6612_M3_IN1, LOW);
        digitalWrite(TB6612_M3_IN2, HIGH);
        analogWrite(Motor_M3_PWM, M3_PWM);
    } else {
        digitalWrite(TB6612_M3_IN1, HIGH);
        digitalWrite(TB6612_M3_IN2, LOW);
        analogWrite(Motor_M3_PWM, -1 * M3_PWM);
    }

    // 设置电机4的正反转及PWM值
    if(M4_PWM > 0) {
        digitalWrite(TB6612_M4_IN1, HIGH);
        digitalWrite(TB6612_M4_IN2, LOW);
        analogWrite(Motor_M4_PWM, M4_PWM);
    } else {
        digitalWrite(TB6612_M4_IN1, LOW);
        digitalWrite(TB6612_M4_IN2, HIGH);
        analogWrite(Motor_M4_PWM, -1 * M4_PWM);
    }
}

// 初始化电机控制引脚为输入或输出模式，并将所有控制引脚设为低电平
void Motor_Init(void)
{
    pinMode(M1_ENCODER_A, INPUT); //M1编码器A引脚，设置为输入模式
    pinMode(M1_ENCODER_B, INPUT); //M1编码器B引脚，设置为输入模式
    pinMode(M2_ENCODER_A, INPUT); //M2编码器A引脚，设置为输入模式
    pinMode(M2_ENCODER_B, INPUT); //M2编码器B引脚，设置为输入模式
    pinMode(M3_ENCODER_A, INPUT); //M3编码器A引脚，设置为输入模式
    pinMode(M3_ENCODER_B, INPUT); //M3编码器B引脚，设置为输入模式
    pinMode(M4_ENCODER_A, INPUT); //M4编码器A引脚，设置为输入模式
    pinMode(M4_ENCODER_B, INPUT); //M4编码器B引脚，设置为输入模式

    pinMode(TB6612_M1_IN1, OUTPUT); //设置两个驱动引脚为输出模式
    pinMode(TB6612_M1_IN2, OUTPUT); 
    pinMode(TB6612_M2_IN1, OUTPUT); //设置两个驱动引脚为输出模式
    pinMode(TB6612_M2_IN2, OUTPUT); 
    pinMode(TB6612_M3_IN1, OUTPUT); //设置两个驱动引脚为输出模式
    pinMode(TB6612_M3_IN2, OUTPUT); 
    pinMode(TB6612_M4_IN1, OUTPUT); //设置两个驱动引脚为输出模式
    pinMode(TB6612_M4_IN2, OUTPUT); 

    pinMode(Motor_M1_PWM, OUTPUT);  //设置使能引脚为输出模式
    pinMode(Motor_M2_PWM, OUTPUT);  //设置使能引脚为输出模式
    pinMode(Motor_M3_PWM, OUTPUT);  //设置使能引脚为输出模式
    pinMode(Motor_M4_PWM, OUTPUT);  //设置使能引脚为输出模式

    //驱动芯片控制引脚全部拉低，确保电机停止
    digitalWrite(TB6612_M1_IN1, LOW);
    digitalWrite(TB6612_M1_IN2, LOW);
    digitalWrite(Motor_M1_PWM, LOW);
    digitalWrite(TB6612_M2_IN1, LOW);
    digitalWrite(TB6612_M2_IN2, LOW);
    digitalWrite(Motor_M2_PWM, LOW);
    digitalWrite(TB6612_M3_IN1, LOW);
    digitalWrite(TB6612_M3_IN2, LOW);
    digitalWrite(Motor_M3_PWM, LOW);
    digitalWrite(TB6612_M4_IN1, LOW);
    digitalWrite(TB6612_M4_IN2, LOW);
    digitalWrite(Motor_M4_PWM, LOW);
}

// 初始化PID控制器的参数，包括比例、积分、微分系数和输出限制
void PID_Init(void)
{
    M1_Motor_PID.k_p = 0.08;
    M1_Motor_PID.k_i = 0.091;
    M1_Motor_PID.k_d = 0.1;
    M1_Motor_PID.out_max = 250;
    M1_Motor_PID.out_min = -250;
    M1_Motor_PID.input = 0;
    M1_Motor_PID.err_x_max = 1000;

    M2_Motor_PID.k_p = 0.08;
    M2_Motor_PID.k_i = 0.091;
    M2_Motor_PID.k_d = 0.1;
    M2_Motor_PID.out_max = 250;
    M2_Motor_PID.out_min = -250;
    M2_Motor_PID.input = 0;
    M2_Motor_PID.err_x_max = 1000;

    M3_Motor_PID.k_p = 0.08;
    M3_Motor_PID.k_i = 0.091;
    M3_Motor_PID.k_d = 0.1;
    M3_Motor_PID.out_max = 250;
    M3_Motor_PID.out_min = -250;
    M3_Motor_PID.input = 0;
    M3_Motor_PID.err_x_max = 1000;

    M4_Motor_PID.k_p = 0.08;
    M4_Motor_PID.k_i = 0.091;
    M4_Motor_PID.k_d = 0.1;
    M4_Motor_PID.out_max = 250;
    M4_Motor_PID.out_min = -250;
    M4_Motor_PID.input = 0;
    M4_Motor_PID.err_x_max = 1000;
}

// PID增量式计算函数，计算PID控制器的输出
void PID_Cal(PID *pid)
{
    float p, i, d;

    pid->err_2 = pid->err_1;
    pid->err_1 = pid->input - pid->feedback;

    p = pid->k_p * pid->err_1;
    i = pid->k_i * pid->err_x;
    d = pid->k_d * (pid->err_1 - pid->err_2);
    pid->err_x += pid->err_1;
    pid->output = p + i + d;
    // 根据PID公式和当前误差计算输出值，然后根据输出范围限制输出值
    if(pid->output > pid->out_max)      pid->output = pid->out_max;
    if(pid->output < pid->out_min)      pid->output = pid->out_min;
    if(pid->err_x > pid->err_x_max)     pid->err_x = pid->err_x_max;
}

// 读取并计算电机的实际速度，用于PID控制器的反馈
void Read_motor_M1(void)
{
    motor_M1_dir = digitalRead(M1_ENCODER_B);
    if(motor_M1_dir == 1)
    {
        motor_M1++;
    }
    else
    {
        motor_M1--;
    }
}
void Read_motor_M2(void)
{
    motor_M2_dir = digitalRead(M2_ENCODER_B);
    if(motor_M2_dir == 1)
    {
        motor_M2++;
    }
    else
    {
        motor_M2--;
    }
}
void Read_motor_M3(void)
{
    motor_M3_dir = digitalRead(M3_ENCODER_B);
    if(motor_M3_dir == 1)
    {
        motor_M3++;
    }
    else
    {
        motor_M3--;
    }
}
void Read_motor_M4(void)
{
    motor_M4_dir = digitalRead(M4_ENCODER_B);
    if(motor_M4_dir == 1)
    {
        motor_M4++;
    }
    else
    {
        motor_M4--;
    }
}

//下降沿捕获中断 并计算速度
void Read_Motor_V(void)
{
    static float M1_Speed = 0, M2_Speed = 0, M3_Speed = 0, M4_Speed = 0;
    float speed_k = 0.3;
    M1_Speed = M1_Motor_PID.feedback;
    M2_Speed = M2_Motor_PID.feedback;
    M3_Speed = M3_Motor_PID.feedback;
    M4_Speed = M4_Motor_PID.feedback;
    unsigned long nowtime = 0;
    motor_M1 = 0;
    motor_M2 = 0;
    motor_M3 = 0;
    motor_M4 = 0;
    nowtime = millis() + 50; //读50毫秒
    attachInterrupt(digitalPinToInterrupt(M1_ENCODER_A), Read_motor_M1, FALLING);
    attachInterrupt(digitalPinToInterrupt(M2_ENCODER_A), Read_motor_M2, FALLING);
    attachInterrupt(digitalPinToInterrupt(M3_ENCODER_A), Read_motor_M3, FALLING);
    attachInterrupt(digitalPinToInterrupt(M4_ENCODER_A), Read_motor_M4, FALLING);
    while(millis() < nowtime); //达到50毫秒关闭中断
    detachInterrupt(digitalPinToInterrupt(M1_ENCODER_A));//右前轮脉冲关中断计数
    detachInterrupt(digitalPinToInterrupt(M2_ENCODER_A));//左前轮脉冲关中断计数
    detachInterrupt(digitalPinToInterrupt(M3_ENCODER_A));//左后轮脉冲关中断计数
    detachInterrupt(digitalPinToInterrupt(M4_ENCODER_A));//右后轮脉冲关中断计数
    V_M1 = ((motor_M1 / 330) * 65 * PI) * 20; //单位mm/s 
    V_M2 = ((motor_M2 / 330) * 65 * PI) * 20; 
    V_M3 = ((motor_M3 / 330) * 65 * PI) * 20;
    V_M4 = ((motor_M4 / 330) * 65 * PI) * 20;
    M1_Motor_PID.feedback = (1 - speed_k) * V_M1 + speed_k * M1_Speed;
    M2_Motor_PID.feedback = -1 * (1 - speed_k) * V_M2 + speed_k * M2_Speed;
    M3_Motor_PID.feedback = -1 * (1 - speed_k) * V_M3 + speed_k * M3_Speed;
    M4_Motor_PID.feedback = (1 - speed_k) * V_M4 + speed_k * M4_Speed;
}