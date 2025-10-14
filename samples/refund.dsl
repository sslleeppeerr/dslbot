// 退改签场景 —— 具体在前，通用在后
INTENT refund {
    // 具体意图：先归类（无输出）
    when contains "退票" then set action = "refund";
    when contains "改签" then set action = "reschedule";

    // 已归类则给出“记录型”提示
    when intent == refund then reply "好的，我记录为 {action}，请提供订单号。";

    // 通用指引
    when intent == refund then reply "请说明你是要退票还是改签，以及订单号。";
}

INTENT fallback {
    when always then reply "不太确定你的意图哦，可以告诉我是物流、退改签还是校园教务相关吗？";
}
