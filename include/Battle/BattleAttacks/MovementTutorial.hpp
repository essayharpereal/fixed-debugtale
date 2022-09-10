//
// Created by cervi on 08/09/2022.
//

#ifndef LAYTON_MOVEMENTTUTORIAL_HPP
#define LAYTON_MOVEMENTTUTORIAL_HPP

namespace BtlAttacks {
    class MovementTutorial;
}

#include "Battle/BattleAttack.hpp"
#include "Battle/Battle.hpp"
#include "Engine/Sprite.hpp"
#include "Engine/Texture.hpp"

namespace BtlAttacks {
    class MovementTutorial : public BattleAttack {
    public:
        MovementTutorial();
        ~MovementTutorial() noexcept override;
        bool update() override;
    private:
        Engine::Texture tutorialTex;
        Engine::Sprite tutorialSpr;
    };
}

#endif //LAYTON_MOVEMENTTUTORIAL_HPP
