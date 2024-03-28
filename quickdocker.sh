#!/bin/bash

# Simple script to get Docker to start automatically.

create() {
    local docker_src="$1"

    local IMAGE=$(sudo docker images | grep rlsmpverify)
    if [[ "$IMAGE" == "" ]];
    then
        if [[ "$docker_src" == "" ]];
        then
            echo "'rlsmpverify' image doesn't exist, yet no path for Dockerfile is provided."
            return 1
        else
            sudo docker build -t rlsmpverify "$docker_src"
            sudo docker create rlsmpverify
        fi
    fi

    # After grep, the string will be something like
    # <containerID> <image_name> <command_invoked> ....
    # Use cut to get the first part.
    local CONTAINER=$(sudo docker ps -a | grep rlsmpverify | cut -d ' ' -f 1)
    if [[ "$CONTAINER" == "" ]];
    then
        echo "No container based on 'rlsmpverify' detected. Perharps you deleted the image or the container?"
    else
        sudo docker start "$CONTAINER"
    fi
}

stop() {
    local CONTAINER=$(sudo docker ps -a | grep rlsmpverify | cut -d ' ' -f 1)
    if [[ "$CONTAINER" == "" ]];
    then
        echo "No container based on 'rlsmpverify' detected."
    else
        sudo docker stop "$CONTAINER"
    fi

    for arg in "$@";
    do
        if [[ "$arg" == "--cleanup" ]];
        then
            sudo docker rm "$CONTAINER"
        fi    
    done
}

OPTION="$1"
BUILD_PARAM="$2"
case "$OPTION" in
    --help)
        echo "A simple script to build a Docker container of this bot and run it."
        echo "Usage: quickdocker.sh [SWITCH]"
        echo ""
        echo "Available SWITCH (default to --build if not provided):"
        echo "--help: Display this message."
        echo "--build [/path/to/project_dir]: Start a container based on the image 'rlsmpverify'. If there's already a container with such image, it'll start that container instead."
        echo "--stop: Stop a container based on the image 'rlsmpverify'. If there are multiple containers, it'll only stop one."
        echo "--remove: Stop a container based on the image 'rlsmpverify' and remove it. You'll need to remove the image on your own."
        echo "--remove-all: Stop a container based on the image 'rlsmpverify' and remove both the container and the image."
        echo ""
        echo "WARNING: If --build is provided, the script SHOULD include a path to the Dockerfile UNLESS an image is already created."
        ;;
    --build | "")
        status=$(create $BUILD_PARAM)
        if ! [[ "$status" == "" ]];
        then
            echo "$status"
            exit 1
        fi
        ;;
    --stop | --remove | --remove-all)
        if ! [[ "$OPTION" == "--stop" ]];
        then
            status=$(stop --cleanup)
        else
            status=$(stop)
        fi

        if ! [[ "$status" == "" ]];
        then
            echo "$status"
        fi

        if [[ "$OPTION" == "--remove-all" ]];
        then
            sudo docker image rm rlsmpverify
        fi
        ;;
    *)
        echo "Unknown option. Use 'bash quickdocker.sh --help' for valid options."
        ;;
esac
