// 校园教务场景 —— 具体在前，通用在后
INTENT campus {
    // 具体问题：先归类（无输出）
    when contains "选课" then set topic = "course";
    when contains "成绩" then set topic = "grade";

    // 已归类则给出“记录型”提示
    when intent == campus then reply "收到，你关注 {topic}。请详细描述你的问题。";

    // 通用问候/引导
    when intent == campus then reply "你好，这里是教务助手，你是要咨询选课还是成绩？";
}

INTENT fallback {
    when always then reply "你好，我是校园助手，可讨论选课、成绩等。请再具体一些~";
}
