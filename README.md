# YuGiOh-Cards-Asset

根据[YGOProDeck](https://ygoprodeck.com/)与[YGOCDB](https://ygocdb.com/)生成游戏王的所有卡牌数据并存储中心图

本项目是[YuGiOh-Cards-Maker](https://github.com/Arshtyi/YuGiOh-Cards-Maker)的上游之一

## 数据格式

> 如果一张卡没有某个属性，这个键值对不会体现在 json 中

|         Key         | Value Type |                                                                            Value                                                                            | Info                                            | 拥有卡片                      |
| :-----------------: | :--------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------: | ----------------------------------------------- | ----------------------------- |
|      uniqueId       |   `int`    |                                                                              -                                                                              | 去除异画因素后，这个卡名的唯一 ID，实际上为卡密 | 所有                          |
|        name         |  `string`  |                                                                              -                                                                              | 卡名，以 cn_name 为准(即 YGOPRO 风格)           | 所有                          |
|         id          |   `int`    |                                                                              -                                                                              | 卡片 ID,实际上是卡密                            | 所有                          |
|     description     |  `string`  |                                                                              -                                                                              | 效果                                            | 所有                          |
| pendulumDescription |  `string`  |                                                                              -                                                                              | 灵摆效果                                        | 灵摆怪兽                      |
|        scale        |   `int`    |                                                                              -                                                                              | 灵摆刻度值,不区别左右                           | 灵摆怪兽                      |
|       linkVal       |   `int`    |                                                                              -                                                                              | 链接值                                          | 链接怪兽                      |
|     linkMarkers     | `string[]` |                                              bottom-left,bottom,bottom-right,left,right,top-left,top,top-right                                              | 拥有的链接箭头                                  | 链接怪兽                      |
|      cardType       |  `string`  |                                                                     monster/spell/trap                                                                      | 卡片类型                                        | 所有                          |
|      attribute      |  `string`  |                                                     light/dark/divine/earth/fire/water/wind/spell/trap                                                      | 卡片属性                                        | 所有                          |
|        race         |  `string`  |                                                   normal/continuous/field/equip/quick-play/ritual/counter                                                   | 魔法陷阱种类                                    | 魔法卡，陷阱卡                |
|         atk         |   `int`    |                                                                              -                                                                              | 怪兽的攻击力，-1 表示?                          | 怪兽卡                        |
|         def         |   `int`    |                                                                              -                                                                              | 怪兽的守备力，-1 表示?                          | 怪兽卡                        |
|        level        |   `int`    |                                                                              -                                                                              | 怪兽的等级或者阶级，-1 表示?                    | 怪兽卡                        |
|      frameType      |  `string`  | normal/normal-pendulum/effect/effect-pendulum/fusion/fusion-pendulum/ritual/ritual-pendulum/synchro/synchro-pendulum/xyz/xyz-pendulum/link/token/spell/trap | 卡片边框类型                                    | 所有                          |
|      typeline       |  `string`  |                                                                              -                                                                              | 情报栏                                          | 怪兽卡                        |
|        limit        |  `object`  |                                                                              -                                                                              | 规制情况，包括 OCG、TCG、MD                     | 所有                          |
| limit/<ocg/tcg/md>  |  `string`  |                                                               forbidden/limited/semi-limited                                                                | OCG/TCG/MD 规制情况                             | 所有                          |
|      cardImage      |   `int`    |                                                                              -                                                                              | 中心图 id 值                                    | 默认为 id 值，一些 token 不同 |
