#include <string.h>
#include <stdint.h>

#define MAX_PAYLOAD 64

struct frame { uint8_t len; uint8_t data[MAX_PAYLOAD]; };

void parse_frame(const uint8_t *wire, struct frame *out) {
    out->len = wire[0];
    memcpy(out->data, wire + 1, out->len);
}

/* NEGATIVE: bounds-checked variant, must not be reported */
int parse_frame_checked(const uint8_t *wire, size_t wire_len, struct frame *out) {
    if (wire_len < 1) return -1;
    if (wire[0] > MAX_PAYLOAD || (size_t)wire[0] + 1 > wire_len) return -1;
    out->len = wire[0];
    memcpy(out->data, wire + 1, out->len);
    return 0;
}
