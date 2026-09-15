// BlockEvents.rightClicked(event => {
//     const player = event.player;
//     const holder = OriginsJS.getHolder(player);
//     if (event.getBlock().hasTag('minecraft:crops')
//         && holder.hasOrigin('rustic:farmer')
//         && !player.isHolding('minecraft:bone_meal')) {
//         event.cancel();
//     }
// })

LootJS.modifiers(event => {
    event.addBlockModifier('#minecraft:crops')
        .matchPlayerCustom(player => {
            const holder = OriginsJS.getHolder(player.etf$getEntity());
            return !holder.hasOrigin('rustic:farmer');
        })
        .modifyLoot(ItemFilter.ANY, item => {
            if (Math.random() < 0.5) {
                return item.withCount(0);
            }
            return item;
        })
})