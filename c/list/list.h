#ifndef __LIST_H
#define __LIST_H

#include <inttypes.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <syslog.h>

#define LIST_ITEM_PTR(list, index) ((list)->root + (index) * (list)->entry_size)
#define LIST_COUNT_BYTES(list, index) ((index) * (list)->entry_size)

typedef struct
{
    void *root;
    uint32_t entry_size;
    uint32_t used;
    uint32_t count;
    pthread_mutex_t mutex;
} list_t;

typedef bool (*list_enumerate_cb)(list_t *, uint32_t, void *, void *);

int list_init(list_t *list, uint32_t entry_size);
int list_destroy(list_t *list);
int list_push(list_t *list, void *value);
void *list_get(list_t *list, uint32_t index);
int list_remove(list_t *list, uint32_t index);
int list_enumerate(list_t *list, list_enumerate_cb cb, void *data);

#endif

