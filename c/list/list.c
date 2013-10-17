#include "list.h"

int list_init(list_t *list, uint32_t entry_size)
{
    void *root;
    if((root = malloc(entry_size)) == NULL)
        return -1;

    list->root = root;
    list->entry_size = entry_size;
    list->used = 0;
    list->count = 1;
    
    pthread_mutex_init(&list->mutex, NULL);
    
    return 0;
}

int list_destroy(list_t *list)
{
    pthread_mutex_destroy(&list->mutex);
    free(list->root);

    return 0;
}

static int list_expand(list_t *list)
{
    uint32_t new_count = list->count * 2;

    // Double the size of the list.
    void *new_ptr = realloc(list->root, LIST_COUNT_BYTES(list, new_count));
    if(new_ptr == NULL)
        return -1;
    
    list->root = new_ptr;
    list->count = new_count;

    return 0;
}

static int list_shrink(list_t *list)
{
    if(list->count <= 1)
        return 0;

    uint32_t new_count = list->count / 2;

    // Halve the size of the list.
    void *new_ptr = realloc(list->root, LIST_COUNT_BYTES(list, new_count));
    if(new_ptr == NULL)
        return -1;

    list->root = new_ptr;
    list->count = new_count;

    return 0;
}

int list_push(list_t *list, void *value)
{
    pthread_mutex_lock(&list->mutex);

    if(list->used >= list->count)
    {
        if(list_expand(list) != 0)
        {
            pthread_mutex_unlock(&list->mutex);
            return -1;
        }
    }

    if(memcpy(LIST_ITEM_PTR(list, list->used),
              value, 
              list->entry_size) == NULL)
    {
        pthread_mutex_unlock(&list->mutex);
        return -2;
    }

    list->used++;

    pthread_mutex_unlock(&list->mutex);

    return 0;
}

void *list_get(list_t *list, uint32_t index)
{
    if(index >= list->used)
        return NULL;

    return LIST_ITEM_PTR(list, index);
}

int list_remove(list_t *list, uint32_t index)
{
    pthread_mutex_lock(&list->mutex);

    void *ptr;
    if((ptr = list_get(list, index)) == NULL)
    {
        pthread_mutex_unlock(&list->mutex);
        return -1;
    }

    list->used--;

    // If we're now empty, no further action is required. There are no 
    // optimizations that need to be performed when we eliminate our last item.
    if(list->used <= 0)
    {
        pthread_mutex_unlock(&list->mutex);
        return 0;
    }

    // Back-shift the items after by one position.

    const uint32_t count = (list->used - index);
    const uint32_t bytes = LIST_COUNT_BYTES(list, count);

    if(memcpy(LIST_ITEM_PTR(list, index), 
              LIST_ITEM_PTR(list, index + 1), 
              bytes) == NULL)
    {
        pthread_mutex_unlock(&list->mutex);

        syslog(LOG_ERR, "Could not back-shift second half. list=[%p]", list);
        return -2;
    }

    // If we're still allocating more than half the allocated space, we're 
    // done.
    if(list->used > list->count / 2)
    {
        pthread_mutex_unlock(&list->mutex);
        return 0;
    }

    // Shrink the allocated memory by half. It's not needed (right now).
    if(list_shrink(list) != 0)
    {
        pthread_mutex_unlock(&list->mutex);

        syslog(LOG_ERR, "Shrink failed. list=[%p]", list);
        return -3;
    }

    pthread_mutex_unlock(&list->mutex);

    return 0;    
}

int list_enumerate(list_t *list, list_enumerate_cb cb, void *context)
{
    uint32_t i = 0;
    while(i < list->used)
    {
        if(cb(list, i, LIST_ITEM_PTR(list, i), context) == false)
            return 0;

        i++;
    }
    
    return 0;
}

