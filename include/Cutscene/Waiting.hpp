//
// Created by cervi on 29/08/2022.
//

#ifndef UNDERTALE_WAITING_HPP
#define UNDERTALE_WAITING_HPP

#include "CutsceneEnums.hpp"

enum WaitingType {
    NONE = 0,
    WAIT_FRAMES,
    WAIT_EXIT,
    WAIT_ENTER,
    WAIT_DIALOGUE_END,
    WAIT_BATTLE_ATTACK,
    WAIT_BATTLE_ACTION
};

class Waiting {
public:
    void waitFrames(int frames);
    void waitExit();
    void waitEnter();
    void waitDialogueEnd();
    void waitBattleAttack();
    void update(CutsceneLocation callingLocation, bool frame);
    bool getBusy() {return currentWait != NONE;}
private:
    WaitingType currentWait = NONE;
    int currentWaitTime = 0;
};

#endif //UNDERTALE_WAITING_HPP
