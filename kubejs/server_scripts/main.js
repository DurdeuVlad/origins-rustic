const $OriginsJS = Java.loadClass('com.iafenvoy.origins.js.binding.OriginsJSBindings');

function hasOriginOrClass(player, originId) {
    if (!player) return false;
    try {
        if ($OriginsJS.hasOrigin(player, originId)) return true;
        let holder = $OriginsJS.getHolder(player);
        if (holder) {
            if (holder.hasOriginInLayer("origins_classes:class", originId)) return true;
            if (holder.hasOriginInLayer("origins:origin", originId)) return true;
            let classId = String(holder.getOriginId("origins_classes:class"));
            if (classId === originId || classId === originId.replace('rustic:', '')) return true;
            let originLayerId = String(holder.getOriginId("origins:origin"));
            if (originLayerId === originId || originLayerId === originId.replace('rustic:', '')) return true;
            let all = holder.getAllOrigins();
            if (all) {
                for (let i = 0; i < all.size(); i++) {
                    let pair = all.get(i);
                    if (pair && pair.size() > 1) {
                        let id = String(pair.get(1));
                        if (id === originId || id === originId.replace('rustic:', '')) return true;
                    }
                }
            }
        }
    } catch (e) {
        console.error("Origins check error: " + e);
    }
    return false;
}

// Gating for watering can (hearthandharvest:watering_can) on blocks
BlockEvents.rightClicked(event => {
    let cancel = false;
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        let player = event.getPlayer();
        if (player && itemId.includes('watering_can')) {
            let isN = hasOriginOrClass(player, 'rustic:nitwit');
            if (isN) {
                player.displayClientMessage(Text.literal("§cNu stăpânești meșteșugul stropirii ogoarelor!"), true);
                player.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                cancel = true;
            }
        }
    } catch (e) {
        console.error("Error in BlockEvents.rightClicked: " + e);
    }
    if (cancel) {
        event.cancel();
    }
});

// Gating for watering can (air/use) and dragonborn firework rocket
ItemEvents.rightClicked(event => {
    let cancel = false;
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        let player = event.getPlayer();
        if (player && itemId.includes('watering_can')) {
            let isN = hasOriginOrClass(player, 'rustic:nitwit');
            if (isN) {
                player.displayClientMessage(Text.literal("§cNu stăpânești meșteșugul stropirii ogoarelor!"), true);
                player.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                cancel = true;
            }
        } else if (itemId === 'minecraft:firework_rocket') {
            if (player && player.isFallFlying() && hasOriginOrClass(player, 'rustic:dragonborn')) {
                player.displayClientMessage(Text.literal("§cZborul de dragon este organic și nu poate fi propulsat cu artificii!"), true);
                player.playSound('minecraft:block.fire.extinguish', 1.0, 1.0);
                cancel = true;
            }
        }
    } catch (e) {
        console.error("Error in ItemEvents.rightClicked: " + e);
    }
    if (cancel) {
        event.cancel();
    }
});

// Gating for butcher's cleaver on attack (deals 0 damage if nitwit)
EntityEvents.beforeHurt(event => {
    try {
        let source = event.getSource();
        if (!source) return;
        let attacker = source.player || source.actual || source.entity;
        if (attacker && attacker.isPlayer()) {
            let item = attacker.mainHandItem || (attacker.getMainHandItem ? attacker.getMainHandItem() : null);
            let itemId = item && item.id ? String(item.id) : '';
            if (itemId.includes('cleaver') || (item.hasTag && (item.hasTag('c:cleaver') || item.hasTag('forge:cleaver')))) {
                let isN = hasOriginOrClass(attacker, 'rustic:nitwit');
                if (isN) {
                    attacker.displayClientMessage(Text.literal("§cNu ai puterea și învățătura de a mânui satârul de măcelar!"), true);
                    attacker.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                    event.setDamage(0);
                }
            }
        }
    } catch (e) {
        console.error("Error in beforeHurt cleaver check: " + e);
    }
});

// Gating for butcher's cleaver on entity right-click interaction
ItemEvents.entityInteracted(event => {
    let cancel = false;
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        let player = event.getPlayer();
        if (itemId.includes('cleaver') || (item.hasTag && (item.hasTag('c:cleaver') || item.hasTag('forge:cleaver')))) {
            let isN = hasOriginOrClass(player, 'rustic:nitwit');
            if (isN) {
                player.displayClientMessage(Text.literal("§cNu ai puterea și învățătura de a mânui satârul de măcelar!"), true);
                player.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                cancel = true;
            }
        }
    } catch (e) {
        console.error("Error in entityInteracted cleaver check: " + e);
    }
    if (cancel) {
        event.cancel();
    }
});

// Debug command to verify player origins and classes
ServerEvents.commandRegistry(event => {
    const { commands: Commands } = event;
    event.register(
        Commands.literal('testnitwit')
            .executes(ctx => {
                let player = ctx.source.player;
                if (!player) return 0;
                let isN = hasOriginOrClass(player, 'rustic:nitwit');
                let holder = $OriginsJS.getHolder(player);
                let all = holder ? holder.getAllOrigins() : null;
                let classId = holder ? holder.getOriginId("origins_classes:class") : null;
                let hasO = $OriginsJS.hasOrigin(player, 'rustic:nitwit');
                console.log("[TESTNITWIT] hasOriginOrClass: " + isN + " | classId: " + classId + " | hasOrigin: " + hasO + " | all: " + all);
                player.tell("§a[TESTNITWIT] Nitwit: " + isN + " (classId: " + classId + ", hasOrigin: " + hasO + ")");
                return 1;
            })
    );
});
