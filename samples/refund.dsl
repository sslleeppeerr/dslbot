//退改签场景DSL

INTENT refund{
    //如果当前意图是refund，回复指导语
    when intent == refund then reply "请说明你是要退票还是改签，以及订单号。";
    //如果包含“退票”“改签”，给出模板化回答，演示set+reply
    when contains "退票" then set action = "refund";
    when contains "改签" then set action = "reschedule";
    when intent == refund then reply "好的，我记录为{action}，请提供订单号。";
}

INTENT fallback{
    //兜底意图
    when always then reply "不太确定你的意图哦，可以告诉我是物流、退改签还是校园教务相关吗？";
}