#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <termios.h>
#include <fcntl.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

MPU6050 mpu;

// Network configuration
#define SERVER_IP "192.168.1.100"  // Replace with your computer's IP
#define SERVER_PORT 8888
int sockfd;
struct sockaddr_in server_addr;

// MPU control/status vars
bool dmpReady = false;
uint8_t mpuIntStatus;
uint8_t devStatus;
uint16_t packetSize;
uint16_t fifoCount;
uint8_t fifoBuffer[64];

// orientation/motion vars
Quaternion q;
VectorInt16 acc;
VectorInt16 gyr;
VectorInt16 accReal;
VectorFloat gravity;

// Control variables
bool state = false;
bool connected = false;

struct timeval start, startc;
long mtime;

// Data packet structure for network transmission
struct SensorData {
    long timestamp;
    int16_t acc_x, acc_y, acc_z;
    int16_t gyr_x, gyr_y, gyr_z;
    float quat_w, quat_x, quat_y, quat_z;
    int16_t linear_acc_x, linear_acc_y, linear_acc_z;
};

// Terminal settings for non-blocking input
struct termios old_tio, new_tio;

// Initialize non-blocking keyboard input
void initKeyboard() {
    tcgetattr(STDIN_FILENO, &old_tio);
    new_tio = old_tio;
    new_tio.c_lflag &= (~ICANON & ~ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &new_tio);
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
}

// Restore terminal settings
void restoreKeyboard() {
    tcsetattr(STDIN_FILENO, TCSANOW, &old_tio);
}

// Check for keyboard input
char getKeyPress() {
    char ch = 0;
    if (read(STDIN_FILENO, &ch, 1) == 1) {
        return ch;
    }
    return 0;
}

// Initialize network connection
bool initNetwork() {
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        printf("Socket creation failed\n");
        return false;
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);
    
    printf("Network initialized. Target: %s:%d\n", SERVER_IP, SERVER_PORT);
    return true;
}

// Send sensor data over network
void sendSensorData(const SensorData& data) {
    if (connected) {
        ssize_t sent = sendto(sockfd, &data, sizeof(data), 0, 
                             (struct sockaddr*)&server_addr, sizeof(server_addr));
        if (sent < 0) {
            printf("Failed to send data\n");
        }
    }
}

void setup() {
    printf("Initializing MPU6050 Network Transmitter...\n");
    
    // Initialize keyboard input
    initKeyboard();
    
    // Initialize MPU6050
    printf("Initializing I2C devices...\n");
    mpu.initialize();
    
    printf("Testing device connections...\n");
    printf(mpu.testConnection() ? "MPU6050 connection successful\n" : "MPU6050 connection failed\n");
    
    // Initialize DMP
    printf("Initializing DMP...\n");
    devStatus = mpu.dmpInitialize();
    
    // Set offsets (calibration values)
    mpu.setXAccelOffset(-2757);
    mpu.setYAccelOffset(417);
    mpu.setZAccelOffset(1191);
    mpu.setXGyroOffset(-609);
    mpu.setYGyroOffset(-474);
    mpu.setZGyroOffset(415);
    
    if (devStatus == 0) {
        printf("Enabling DMP...\n");
        mpu.setDMPEnabled(true);
        mpuIntStatus = mpu.getIntStatus();
        printf("DMP ready!\n");
        dmpReady = true;
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        printf("DMP Initialization failed (code %d)\n", devStatus);
        return;
    }
    
    // Initialize network
    if (initNetwork()) {
        printf("Network ready!\n");
    } else {
        printf("Network initialization failed!\n");
        return;
    }
    
    gettimeofday(&start, NULL);
    gettimeofday(&startc, NULL);
    
    printf("\n=== MPU6050 Real-time Data Transmitter ===\n");
    printf("Commands:\n");
    printf("  's' - Start/Stop data transmission\n");
    printf("  'q' - Quit program\n");
    printf("  'r' - Reset timestamp\n");
    printf("\nSystem ready. Press 's' to start data transmission...\n");
}

void loop() {
    // Check for keyboard input
    char key = getKeyPress();
    
    if (key == 's' || key == 'S') {
        state = !state;
        connected = state;
        
        if (state) {
            printf("\n>>> Starting data transmission...\n");
            gettimeofday(&startc, NULL);
        } else {
            printf("\n>>> Stopping data transmission...\n");
        }
    } else if (key == 'q' || key == 'Q') {
        printf("\n>>> Exiting program...\n");
        restoreKeyboard();
        close(sockfd);
        exit(0);
    } else if (key == 'r' || key == 'R') {
        printf("\n>>> Resetting timestamp...\n");
        gettimeofday(&startc, NULL);
    }
    
    // Process MPU6050 data
    if (!dmpReady) return;
    
    fifoCount = mpu.getFIFOCount();
    
    if (fifoCount == 1024) {
        mpu.resetFIFO();
        printf("FIFO overflow!\n");
    } else if (fifoCount >= 42) {
        // Read sensor data
        mpu.getFIFOBytes(fifoBuffer, packetSize);
        
        // Calculate timestamp
        struct timeval current;
        gettimeofday(&current, NULL);
        mtime = ((current.tv_sec - startc.tv_sec) * 1000 + 
                (current.tv_usec - startc.tv_usec) / 1000);
        
        // Extract sensor data
        mpu.dmpGetAccel(&acc, fifoBuffer);
        mpu.dmpGetGyro(&gyr, fifoBuffer);
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&accReal, &acc, &gravity);
        
        // Prepare data packet
        SensorData data;
        data.timestamp = mtime;
        data.acc_x = acc.x;
        data.acc_y = acc.y;
        data.acc_z = acc.z;
        data.gyr_x = gyr.x;
        data.gyr_y = gyr.y;
        data.gyr_z = gyr.z;
        data.quat_w = q.w;
        data.quat_x = q.x;
        data.quat_y = q.y;
        data.quat_z = q.z;
        data.linear_acc_x = accReal.x;
        data.linear_acc_y = accReal.y;
        data.linear_acc_z = accReal.z;
        
        // Send data if transmission is active
        if (state) {
            sendSensorData(data);
            // Print data every 100ms to avoid flooding the console
            static long last_print = 0;
            if (mtime - last_print > 100) {
                printf("Time: %6ld ms | Acc: %6d,%6d,%6d | Quat: %6.3f,%6.3f,%6.3f,%6.3f | Status: TRANSMITTING\n", 
                       mtime, acc.x, acc.y, acc.z, q.w, q.x, q.y, q.z);
                last_print = mtime;
            }
        } else {
            // Print status every 1000ms when not transmitting
            static long last_status = 0;
            if (mtime - last_status > 1000) {
                printf("Time: %6ld ms | Status: READY (Press 's' to start transmission)\n", mtime);
                last_status = mtime;
            }
        }
    }
}

int main() {
    setup();
    
    while (1) {
        loop();
        usleep(1000); // 1ms delay
    }
    
    restoreKeyboard();
    close(sockfd);
    return 0;
} 