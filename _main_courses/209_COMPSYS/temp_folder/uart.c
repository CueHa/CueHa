#define F_CPU 2000000UL

#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

#define BAUD 9600
#define UBRR (F_CPU / (16 * BAUD) - 1)

// Application values (fixed-point) 
#define RMS_V_TENTHS   145   // 14.5 V -> XX.X
#define PEAK_CURRENT   125   // 125 A  -> XXX
#define POWER_CENTI    160   // 1.60 W -> X.XX

//
static inline void usart_init(uint16_t ubrr) {
    UBRR0H = (uint8_t)(ubrr >> 8);
    UBRR0L = (uint8_t)ubrr;
    UCSR0B = (1 << RXEN0) | (1 << TXEN0);     // enable RX & TX although RX is unused
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);  // 8 data bits, no parity, 1 stop bit
}

static inline void usart_tx_char(uint8_t c) {
    while (!(UCSR0A & (1 << UDRE0))) {;}
    UDR0 = c;
}

static void usart_tx_str(const char *s) {
    while (*s) usart_tx_char((uint8_t)*s++);
}

//
static void usart_tx_uint(unsigned v, uint8_t width) {
    char buf[10];
    uint8_t i = 0;

    // extract digits in reverse order
    do {
        buf[i++] = '0' + (v % 10u);
        v /= 10u;
    } while (v && i < sizeof buf);

    // pad with leading zeros if needed
    while (i < width && i < sizeof buf) buf[i++] = '0';

    // send in correct order
    while (i) usart_tx_char(buf[--i]);
}

// print functions for each measurement
static void print_rms_voltage(uint16_t tenths) {
    uint16_t whole = tenths / 10u;     // XX
    uint16_t frac  = tenths % 10u;     // X
    usart_tx_str("RMS Voltage is: ");
    usart_tx_uint(whole, 0);
    usart_tx_char('.');
    usart_tx_uint(frac, 1);            // always 1 digit
    usart_tx_str("\r\n");
}

static void print_peak_current(uint16_t amps) {
    usart_tx_str("Peak Current is: ");
    usart_tx_uint(amps, 0);            // integer, up to 3 digits
    usart_tx_str("\r\n");
}

static void print_power(uint16_t centi) {
    uint16_t whole = centi / 100u;     // X
    uint16_t frac  = centi % 100u;     // XX
    usart_tx_str("Power is: ");
    usart_tx_uint(whole, 0);
    usart_tx_char('.');
    usart_tx_uint(frac, 2);            // always 2 digits
    usart_tx_str("\r\n");
}

int main(void) {
    usart_init(UBRR);                     // 9600 @ 2 MHz

    for (;;) {
        print_rms_voltage(RMS_V_TENTHS);
        print_peak_current(PEAK_CURRENT);
        print_power(POWER_CENTI);
        usart_tx_str("\r\n");           // blank line between groups
        _delay_ms(1000);                // print every 1 s with a simple delay for now
    }
}
