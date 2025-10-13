//物流场景DSL
INTENT logistics{
    //如果当前意图是logistics且包含“快递/物流/单号”等关键词，回复指导语
    when intent == logistics then reply "请提供快递单号，我来帮你查询进度~";
    //如果包含“查询”且包含“到哪了”，给出模板化回答，演示set+reply
    when contains "到哪了" then set last_question = "where";
    when intent == logistics then reply "我已记录你的问题类型：{last_question}，请继续提供单号。";
}

INTENT fallback{
    //兜底意图
    when always then reply "我暂时不确定你的需求，是关于物流、退改签还是校园教务？可以提供更多信息吗？";
}