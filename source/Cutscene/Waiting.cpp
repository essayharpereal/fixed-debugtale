//
// Created by cervi on 30/08/2022.
//

#include "Cutscene/Waiting.hpp"

void Waiting::waitFrames(int frames) {
    currentWait = WAIT_FRAMES;
    currentWaitTime = frames;
}

void Waiting::waitLoad() {
    currentWait = WAIT_LOAD;
}

void Waiting::update(CutsceneLocation callingLocation) {
    if (currentWait == NONE)
        return;

    if (currentWait == WAIT_FRAMES) {
        currentWaitTime -= 1;
        if (currentWaitTime <= 0) {
            currentWait = NONE;
        }
    } else if (currentWait == WAIT_LOAD) {
        if (callingLocation == LOAD_ROOM)
            currentWait = NONE;
    }
}
