#define F_CPU 2000000UL

// the micro controller I/O and register names.
#include <avr/io.h>
// to use delay function
#include <util/delay.h>
// to use integer operations.
#include <stdint.h>

#define BAUD 9600
#define UBRR ((F_CPU + (8UL * BAUD)) / (16UL * BAUD) - 1)

// Application values (fixed-point)
#define RMS_V 145        // 14.5 V -> XX.X
#define PEAK_CURRENT 125 // 125 A  -> XXX
#define POWER 160        // 1.60 W -> X.XX

// Initialize UART for 9600 BAUD at 8N1 at no parity.
static void uart_init(uint16_t ubrr)
{
    UBRR0H = (uint8_t)(ubrr >> 8);
    UBRR0L = (uint8_t)ubrr;
    UCSR0B = (1 << TXEN0);                  // enable TX
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00); // 8 data bits, no parity, 1 stop bit
}

// the one that stores data it receives as an input to UDR0 register.
static void uart_tx_char(uint8_t c)
{
    // while UDRE0 (transmit ready flag) zero, do nothing.
    while (!(UCSR0A & (1 << UDRE0)))
    {
        ;
    }
    // else, transmit data.
    UDR0 = c;
}

// helper functions
static void uart_tx_str(const char *s)
{
    while (*s)
        uart_tx_char((uint8_t)*s++);
}

//
static void uart_tx_uint(unsigned data, uint8_t width)
{
    char buf[10];
    uint8_t i = 0;

    // extract digits in reverse order
    do
    {
        buf[i++] = '0' + (v % 10u);
        v /= 10u;
    } while (v && i < sizeof buf);

    // pad with leading zeros if needed
    while (i < width && i < sizeof buf)
        buf[i++] = '0';

    // send in correct order
    while (i)
        uart_tx_char(buf[--i]);
}

// print functions for each measurement
static void print_rms_voltage(uint16_t tenths)
{
    uint16_t whole = tenths / 10u; // XX
    uint16_t frac = tenths % 10u;  // X
    uart_tx_str("RMS Voltage is: ");
    uart_tx_uint(whole, 0);
    uart_tx_char('.');
    uart_tx_uint(frac, 1); // always 1 digit
    uart_tx_str("\r\n");
}

static void print_peak_current(uint16_t amps)
{
    uart_tx_str("Peak Current is: ");
    uart_tx_uint(amps, 0); // integer, up to 3 digits
    uart_tx_str("\r\n");
}

static void print_power(uint16_t centi)
{
    uint16_t whole = centi / 100u; // X
    uint16_t frac = centi % 100u;  // XX
    uart_tx_str("Power is: ");
    uart_tx_uint(whole, 0);
    uart_tx_char('.');
    uart_tx_uint(frac, 2); // always 2 digits
    uart_tx_str("\r\n");
}

// main loop to print the required format.
int main(void)
{
    uart_init(UBRR); // 9600 @ 2 MHz

    for (;;)
    {
        print_rms_voltage(RMS_V);
        print_peak_current(PEAK_CURRENT);
        print_power(POWER);
        uart_tx_str("\r\n"); // blank line between groups
        _delay_ms(1000);     // print every 1 s with a simple delay for now
    }
}
