// Server-side logic for Farmer origin: right-click harvest+replant and non-farmer 50% drop reduction
const $OriginsJS_Farmer = Java.loadClass('com.iafenvoy.origins.js.binding.OriginsJSBindings');
const $NeoForge_Farmer = Java.loadClass('net.neoforged.neoforge.common.NeoForge');

let $CropBlock = null;
let $CocoaBlock = null;
let $NetherWartBlock = null;
let $Block = null;
let $BlockTags = null;
let $SoundEvents = null;
let $SoundSource = null;
let $EquipmentSlot = null;
let $BlockDropsEvent = null;

try {
    $CropBlock = Java.loadClass('net.minecraft.world.level.block.CropBlock');
    $CocoaBlock = Java.loadClass('net.minecraft.world.level.block.CocoaBlock');
    $NetherWartBlock = Java.loadClass('net.minecraft.world.level.block.NetherWartBlock');
    $Block = Java.loadClass('net.minecraft.world.level.block.Block');
    $BlockTags = Java.loadClass('net.minecraft.tags.BlockTags');
    $SoundEvents = Java.loadClass('net.minecraft.sounds.SoundEvents');
    $SoundSource = Java.loadClass('net.minecraft.sounds.SoundSource');
    $EquipmentSlot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot');
    $BlockDropsEvent = Java.loadClass('net.neoforged.neoforge.event.level.BlockDropsEvent');
} catch (e) {
    console.error("[FARMER] Error loading Minecraft/NeoForge classes: " + e);
}

function isFarmer(player) {
    if (!player) return false;
    try {
        if (typeof hasOriginOrClass === 'function') {
            return hasOriginOrClass(player, 'rustic:farmer');
        }
        if ($OriginsJS_Farmer && $OriginsJS_Farmer.hasOrigin(player, 'rustic:farmer')) return true;
        let holder = $OriginsJS_Farmer ? $OriginsJS_Farmer.getHolder(player) : null;
        if (holder) {
            if (holder.hasOriginInLayer("origins_classes:class", "rustic:farmer")) return true;
            if (holder.hasOriginInLayer("origins:origin", "rustic:farmer")) return true;
            let classId = String(holder.getOriginId("origins_classes:class"));
            if (classId === 'rustic:farmer' || classId === 'farmer') return true;
            let originId = String(holder.getOriginId("origins:origin"));
            if (originId === 'rustic:farmer' || originId === 'farmer') return true;
        }
    } catch (e) {
        console.error("Error checking farmer origin: " + e);
    }
    return false;
}

function isCrop(block, state) {
    if (!block || !state) return false;
    try {
        if ($CropBlock && block instanceof $CropBlock) return true;
        if ($CocoaBlock && block instanceof $CocoaBlock) return true;
        if ($NetherWartBlock && block instanceof $NetherWartBlock) return true;
        if (state.is && $BlockTags && state.is($BlockTags.CROPS)) return true;
        let id = block.getDescriptionId ? String(block.getDescriptionId()) : '';
        if (id.includes('crop') || id.includes('wheat') || id.includes('carrot') || id.includes('potato') || id.includes('beetroot')) return true;
    } catch (e) {}
    return false;
}

function isCropMature(block, state) {
    if (!block || !state) return false;
    try {
        if ($CropBlock && block instanceof $CropBlock) {
            return block.isMaxAge(state);
        }
        if ($CocoaBlock && block instanceof $CocoaBlock) {
            return state.getValue($CocoaBlock.AGE) >= 2;
        }
        if ($NetherWartBlock && block instanceof $NetherWartBlock) {
            return state.getValue($NetherWartBlock.AGE) >= 3;
        }
        let props = state.getValues ? state.getValues() : null;
        if (props) {
            let iter = props.entrySet().iterator();
            while (iter.hasNext()) {
                let entry = iter.next();
                if (entry.getKey().getName() === 'age') {
                    let val = Number(entry.getValue());
                    let maxVal = -1;
                    let vIter = entry.getKey().getPossibleValues().iterator();
                    while (vIter.hasNext()) {
                        let v = Number(vIter.next());
                        if (v > maxVal) maxVal = v;
                    }
                    return maxVal > 0 && val >= maxVal;
                }
            }
        }
    } catch (e) {
        console.error("Error checking crop maturity: " + e);
    }
    return false;
}

function getReplantedState(block, state) {
    try {
        if ($CropBlock && block instanceof $CropBlock) {
            return block.getStateForAge(0);
        }
        if ($CocoaBlock && block instanceof $CocoaBlock) {
            return state.setValue($CocoaBlock.AGE, 0);
        }
        if ($NetherWartBlock && block instanceof $NetherWartBlock) {
            return state.setValue($NetherWartBlock.AGE, 0);
        }
        let props = state.getValues ? state.getValues() : null;
        if (props) {
            let iter = props.entrySet().iterator();
            while (iter.hasNext()) {
                let entry = iter.next();
                let prop = entry.getKey();
                if (prop.getName() === 'age') {
                    return state.setValue(prop, prop.getPossibleValues().iterator().next());
                }
            }
        }
    } catch (e) {
        console.error("Error getting replanted state: " + e);
    }
    return block.defaultBlockState();
}

function isHoeOrEmptyHand(itemStack) {
    if (!itemStack || itemStack.isEmpty()) return true;
    let itemId = itemStack.kjs$getId ? String(itemStack.kjs$getId()) : (itemStack.id ? String(itemStack.id) : '');
    if (itemId.includes('hoe')) return true;
    if (itemStack.hasTag && (itemStack.hasTag('c:tools/hoe') || itemStack.hasTag('minecraft:hoes') || itemStack.hasTag('forge:tools/hoes'))) return true;
    return false;
}

// Right-click harvest and replant for Farmer, and lockout for non-farmers
BlockEvents.rightClicked(event => {
    try {
        let blockContainer = event.getBlock();
        if (!blockContainer) return;
        let blockState = blockContainer.getBlockState ? blockContainer.getBlockState() : null;
        if (!blockState) return;
        let block = blockState.getBlock();
        if (!isCrop(block, blockState)) return;

        let player = event.getPlayer();
        if (!player) return;

        let item = event.getItem();
        let allowsHarvestInteraction = isHoeOrEmptyHand(item);

        let farmer = isFarmer(player);

        if (!farmer) {
            // Non-farmers cannot right-click-harvest crops; right-click should do nothing special
            if (allowsHarvestInteraction) {
                event.cancel();
            }
            return;
        }

        // Player is a Farmer using a hoe or empty hand
        if (allowsHarvestInteraction) {
            if (!isCropMature(block, blockState)) {
                return;
            }

            let level = event.getLevel();
            if (level && level.isClientSide && level.isClientSide()) {
                event.cancel();
                return;
            }
            let serverLevel = level.asKubeJSServerLevel ? level.asKubeJSServerLevel() : level;
            let pos = event.getPos();
            let heldItem = player.getMainHandItem();

            // 1. Collect loot drops for the mature crop
            let drops = $Block.getDrops(blockState, serverLevel, pos, null, player, heldItem);

            // 2. Replant crop to age 0
            let replantedState = getReplantedState(block, blockState);
            serverLevel.setBlock(pos, replantedState, 3);

            // 3. Deduct 1 seed/crop from drops for the replanted crop, and drop remaining items
            let seedDeducted = false;
            if (drops) {
                for (let i = 0; i < drops.size(); i++) {
                    let drop = drops.get(i);
                    let dropId = drop.kjs$getId ? String(drop.kjs$getId()) : (drop.getItem ? String(drop.getItem()) : '');
                    if (!seedDeducted) {
                        if (dropId.includes('seed') || dropId.includes('carrot') || dropId.includes('potato') || dropId.includes('wart') || dropId.includes('cocoa')) {
                            drop.shrink(1);
                            seedDeducted = true;
                        }
                    }
                    if (drop.getCount() > 0) {
                        $Block.popResource(serverLevel, pos, drop);
                    }
                }
            }

            // 4. Play crop breaking/planting sound
            if ($SoundEvents && $SoundSource) {
                serverLevel.playSound(null, pos, $SoundEvents.CROP_BREAK, $SoundSource.BLOCKS, 1.0, 1.0);
            }

            // 5. Damage hoe if a hoe was used
            if (heldItem && !heldItem.isEmpty() && $EquipmentSlot) {
                try {
                    heldItem.hurtAndBreak(1, player, $EquipmentSlot.MAINHAND);
                } catch (e) {}
            }

            // 6. Swing player hand
            player.swing(event.getHand(), true);

            // 7. Cancel event to prevent duplicate vanilla or mod actions
            event.cancel();
        }
    } catch (e) {
        console.error("Error in Farmer BlockEvents.rightClicked: " + e);
    }
});

// Non-farmer normal breaking penalty: 50% chance of getting no drops at all
if ($NeoForge_Farmer && $BlockDropsEvent) {
    let blockDropsConsumer = (event) => {
        try {
            let breaker = event.getBreaker();
            if (!breaker || !breaker.isPlayer()) return;

            let state = event.getState();
            if (!state) return;
            let block = state.getBlock();
            if (!isCrop(block, state)) return;

            let isF = isFarmer(breaker);
            if (!isF) {
                // Non-farmer: 50% chance of receiving zero drops
                if (Math.random() < 0.5) {
                    let drops = event.getDrops();
                    if (drops) {
                        drops.clear();
                    }
                    event.setCanceled(true);
                }
            }
        } catch (e) {
            console.error("Error in Farmer BlockDropsEvent: " + e);
        }
    };

    $NeoForge_Farmer.EVENT_BUS['addListener(java.lang.Class,java.util.function.Consumer)']($BlockDropsEvent, blockDropsConsumer);
}
