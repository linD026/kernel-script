#ifndef __FTRACE_H__
#define __FTRACE_H__

#include <stdio.h>
#include <stdlib.h>

#define ftrace_stream stdout
#define FTRACE_DIR "/sys/kernel/tracing"

#define ftrace_print(format, ...) \
    fprintf(ftrace_stream, "\e[32m[FTRACE]\e[0m " format, ##__VA_ARGS__)

#define ftrace_err(format, ...)                                          \
    do {                                                                 \
        fprintf(ftrace_stream,                                           \
                "\e[32m[FTRACE]\e[0m %s:%d:%s: \e[31m" format "\e[0m\n", \
                __FILE__, __LINE__, __func__, ##__VA_ARGS__);            \
        exit(EXIT_FAILURE);                                              \
    } while (0)

#define ftrace_write_file(input, file)                          \
    do {                                                        \
        ftrace_print("echo " input " > " FTRACE_DIR file "\n"); \
        system("echo " input " > " FTRACE_DIR file);            \
    } while (0)

static void ftrace_system(const char *command)
{
    ftrace_print("%s \n", command);
    system(command);
}

static void ftrace_info(void)
{
    // TODO
}

static void ftrace_set_tracing_on(void)
{
    ftrace_write_file("1", "/tracing_on");
}

static void ftrace_unset_tracing_on(void)
{
    ftrace_write_file("0", "/tracing_on");
}

static void ftrace_set_pid(unsigned int pid)
{
    char cmd[101] = { 0 };

    sprintf(cmd, "echo %d > " FTRACE_DIR "/set_ftrace_pid", pid);
    cmd[100] = '\0';
    ftrace_system(cmd);
}

enum {
    FTRACER_FUNCTION,
    FTRACER_FUNCTION_GRAPH,
};

static void ftrace_set_tracer(int type)
{
    switch (type) {
    case FTRACER_FUNCTION:
        ftrace_write_file("function", "/current_tracer");
        break;
    case FTRACER_FUNCTION_GRAPH:
        ftrace_write_file("function_graph", "/current_tracer");
        break;
    default:
        ftrace_err("type unkown");
    }
}

static void ftrace_init(int tracer_type)
{
    ftrace_set_tracer(tracer_type);
    ftrace_set_pid(getpid());
    ftrace_info();
    ftrace_set_tracing_on();
}

static void ftrace_exit(void)
{
    ftrace_unset_tracing_on();
    ftrace_system("cat " FTRACE_DIR "/trace > ftrace.log");
}

#endif /* __FTRACE_H__ */
