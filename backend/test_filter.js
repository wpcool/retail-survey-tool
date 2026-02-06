// 模拟前端筛选逻辑
const products = [
    {
        name: "好福原汁花蛤肉",
        category_level1_name: "生鲜",
        category_level2_name: "水产",
        category_level3_name: "加工水产",
        category_level4_name: "去壳加工水产"
    },
    {
        name: "测试商品",
        category_level1_name: "食品杂货",
        category_level2_name: "零食",
        category_level3_name: "坚果",
        category_level4_name: "开心果"
    }
];

// 模拟筛选条件
const level1 = "生鲜";
const level2 = "水产";
const level3 = "加工水产";
const level4 = "去壳加工水产";

const filtered = products.filter(p => {
    const matchL1 = !level1 || p.category_level1_name === level1;
    const matchL2 = !level2 || p.category_level2_name === level2;
    const matchL3 = !level3 || p.category_level3_name === level3;
    const matchL4 = !level4 || p.category_level4_name === level4;
    const result = matchL1 && matchL2 && matchL3 && matchL4;
    console.log(`商品: ${p.name}`);
    console.log(`  L1=${p.category_level1_name} matchL1=${matchL1}`);
    console.log(`  L2=${p.category_level2_name} matchL2=${matchL2}`);
    console.log(`  L3=${p.category_level3_name} matchL3=${matchL3}`);
    console.log(`  L4=${p.category_level4_name} matchL4=${matchL4}`);
    console.log(`  结果: ${result}`);
    return result;
});

console.log(`\n筛选结果: ${filtered.length} 个商品`);
