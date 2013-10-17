#include <stdio.h>

#include "list.h"

static bool enumerate_cb(list_t *list, 
                         uint32_t index, 
                         void *value, 
                         void *context)
{
    char *text = (char *)value;
    printf("Item (%" PRIu8 "): [%s]\n", index, text);

    // Return false to stop enumeration (enumeration will return successful).
    return true;
}

int main()
{
    list_t list;
    const uint32_t entry_width = 20;
    
    if(list_init(&list, entry_width) != 0)
    {
        printf("Could not initialize list.\n");
        return 1;
    }

    char text[20];
    const uint8_t count = 10;
    uint8_t i = 0;
    while(i < count)
    {
        snprintf(text, 20, "Test: %" PRIu8, i);
        printf("Pushing: %s\n", text);

        if(list_push(&list, text) != 0)
        {
            printf("Could not push item.\n");
            return 2;
        }
    
        i++;
    }

    printf("\n");

    // NOTE: For efficiency, this is a reference to within the list. If you
    //       want a copy, make a copy. If you want to make sure this is thread-
    //       safe, use a lock.
    void *retrieved;
    if((retrieved = list_get(&list, 5)) == NULL)
    {
        printf("Could not retrieve item.\n");
        return 3;
    }

    printf("Retrieved: %s\n", (char *)retrieved);
    printf("Removing.\n");

    if(list_remove(&list, 5) != 0)
    {
        printf("Could not remove item.\n");
        return 4;
    }

    printf("\n");
    printf("Enumerating:\n");

    if(list_enumerate(&list, enumerate_cb, NULL) != 0)
    {
        printf("Could not enumerate list.\n");
        return 5;
    }

    if(list_destroy(&list) != 0)
    {
        printf("Could not destroy list.\n");
        return 6;
    }

    return 0;
}

