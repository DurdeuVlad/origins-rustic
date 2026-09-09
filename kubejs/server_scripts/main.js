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

// Gating for watering can (hearthandharvest:watering_can)
BlockEvents.rightClicked(event => {
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        let player = event.getPlayer();
        if (player && itemId.includes('watering_can')) {
            let isN = hasOriginOrClass(player, 'rustic:nitwit');
            console.log("[DEBUG] BlockEvents.rightClicked: player=" + player.username + " item=" + itemId + " isNitwit=" + isN);
            if (isN) {
                player.displayClientMessage(Text.literal("§cNu stăpânești meșteșugul stropirii ogoarelor!"), true);
                player.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                event.cancel();
            }
        }
    } catch (e) {
        if (String(e).includes('EventExit')) throw e;
        console.error("Error in BlockEvents.rightClicked: " + e);
    }
});

ItemEvents.rightClicked(event => {
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        let player = event.getPlayer();
        if (player && itemId.includes('watering_can')) {
            let isN = hasOriginOrClass(player, 'rustic:nitwit');
            console.log("[DEBUG] ItemEvents.rightClicked: player=" + player.username + " item=" + itemId + " isNitwit=" + isN);
            if (isN) {
                player.displayClientMessage(Text.literal("§cNu stăpânești meșteșugul stropirii ogoarelor!"), true);
                player.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                event.cancel();
            }
        }
    } catch (e) {
        if (String(e).includes('EventExit')) throw e;
        console.error("Error in ItemEvents.rightClicked: " + e);
    }
});

// Gating for butcher's cleaver (butchery:iron_cleaver, butchery:netherite_cleaver, etc.) on attack
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
                console.log("[DEBUG] beforeHurt: attacker=" + attacker.username + " item=" + itemId + " isNitwit=" + isN);
                if (isN) {
                    attacker.displayClientMessage(Text.literal("§cNu ai puterea și învățătura de a mânui satârul de măcelar!"), true);
                    attacker.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                    event.setDamage(0);
                    event.cancel();
                }
            }
        }
    } catch (e) {
        if (String(e).includes('EventExit')) throw e;
        console.error("Error in beforeHurt cleaver check: " + e);
    }
});

ItemEvents.entityInteracted(event => {
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        let player = event.getPlayer();
        if (itemId.includes('cleaver') || (item.hasTag && (item.hasTag('c:cleaver') || item.hasTag('forge:cleaver')))) {
            let isN = hasOriginOrClass(player, 'rustic:nitwit');
            console.log("[DEBUG] entityInteracted: player=" + (player ? player.username : "null") + " item=" + itemId + " isNitwit=" + isN);
            if (isN) {
                player.displayClientMessage(Text.literal("§cNu ai puterea și învățătura de a mânui satârul de măcelar!"), true);
                player.playSound('minecraft:block.chest.locked', 1.0, 1.0);
                event.cancel();
            }
        }
    } catch (e) {
        if (String(e).includes('EventExit')) throw e;
        console.error("Error in entityInteracted cleaver check: " + e);
    }
});

// Restriction for Dragonborn firework rocket flight boost
ItemEvents.rightClicked(event => {
    try {
        let item = event.getItem();
        let itemId = item && item.id ? String(item.id) : '';
        if (itemId === 'minecraft:firework_rocket') {
            let player = event.getPlayer();
            if (player.isFallFlying() && hasOriginOrClass(player, 'rustic:dragonborn')) {
                player.displayClientMessage(Text.literal("§cZborul de dragon este organic și nu poate fi propulsat cu artificii!"), true);
                player.playSound('minecraft:block.fire.extinguish', 1.0, 1.0);
                event.cancel();
            }
        }
    } catch (e) {
        if (String(e).includes('EventExit')) throw e;
        console.error("Error in firework check: " + e);
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


