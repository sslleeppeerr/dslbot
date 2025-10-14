// 物流场景 —— 先处理具体，再处理通用（两阶段执行能先 set 再 reply）
INTENT logistics {
    // 1) 具体追问：记录问题类型（本轮不输出）
    when contains "到哪了" then set last_question = "where";

    // 2) 捕获承运方线索（可选，先记录，便于后面的模板渲染）
    when contains "SF" then set carrier = "顺丰";
    when contains "顺丰" then set carrier = "顺丰";
    when contains "中通" then set carrier = "中通";
    when contains "圆通" then set carrier = "圆通";
    when contains "申通" then set carrier = "申通";
    when contains "京东" then set carrier = "京东";
    when contains "邮政" then set carrier = "邮政";

    // 3) 只要用户给出“单号”，这一轮就优先给出“查询结果”的回复（覆盖通用提示）
    //    注意：这条必须放在通用 reply 之前，保证优先命中
    when contains "单号" then reply "收到你的单号，{carrier}正在运输中（模拟查询）。如需更详细轨迹，请发送更完整的单号或者截图。";

    // 4) 若本轮只是问法/追问（比如“到哪了”），给出“已记录类型”的提示
    when intent == logistics then reply "我已记录你的问题类型：{last_question}，请继续提供单号。";

    // 5) 首次进入/无任何线索时的引导
    when intent == logistics then reply "请提供快递单号，我来帮你查询进度~";
}

INTENT fallback {
    when always then reply "我暂时不确定你的需求，是关于物流、退改签还是校园教务？可以提供更多信息吗？";
}
