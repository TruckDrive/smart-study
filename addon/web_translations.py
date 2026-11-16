"""Translations used by HTML/JavaScript surfaces.

Kept separate from the large native-UI catalog in ``locales.py`` while using
the same exact-English-source lookup contract.
"""

from typing import Dict


WEB_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "For your safety, potentially unsafe HTML was kept as text or removed. It could otherwise run code. Normal text and safe links still work.": {
        "de": "Zu deiner Sicherheit wurde potenziell unsicheres HTML als Text beibehalten oder entfernt. Es könnte sonst Code ausführen. Normaler Text und sichere Links funktionieren weiterhin.",
        "es": "Por tu seguridad, el HTML potencialmente peligroso se ha conservado como texto o eliminado. De lo contrario, podría ejecutar código. El texto normal y los enlaces seguros siguen funcionando.",
        "ko": "안전을 위해 위험할 수 있는 HTML을 텍스트로 유지하거나 제거했습니다. 그렇지 않으면 코드가 실행될 수 있습니다. 일반 텍스트와 안전한 링크는 계속 사용할 수 있습니다.",
        "pt": "Para sua segurança, o HTML potencialmente perigoso foi mantido como texto ou removido. Caso contrário, poderia executar código. Texto normal e links seguros continuam funcionando.",
        "fr": "Pour votre sécurité, le HTML potentiellement dangereux a été conservé comme texte ou supprimé. Il pourrait sinon exécuter du code. Le texte normal et les liens sûrs fonctionnent toujours.",
        "vi": "Để bảo vệ bạn, HTML có thể không an toàn đã được giữ dưới dạng văn bản hoặc bị xóa. Nếu không, nội dung đó có thể chạy mã. Văn bản thông thường và liên kết an toàn vẫn hoạt động.",
        "zh": "为保障安全，可能不安全的 HTML 已保留为文本或被移除，否则可能执行代码。普通文本和安全链接仍可正常使用。",
        "hi": "आपकी सुरक्षा के लिए, संभावित असुरक्षित HTML को पाठ के रूप में रखा गया या हटा दिया गया है। अन्यथा यह कोड चला सकता था। सामान्य पाठ और सुरक्षित लिंक अब भी काम करते हैं।",
        "pl": "Dla Twojego bezpieczeństwa potencjalnie niebezpieczny HTML zachowano jako tekst lub usunięto. W przeciwnym razie mógłby uruchomić kod. Zwykły tekst i bezpieczne linki nadal działają.",
    },
    "Smart Study Settings": {
        "de": "Smart Study-Einstellungen", "es": "Ajustes de Smart Study", "ko": "Smart Study 설정", "pt": "Configurações do Smart Study",
        "fr": "Paramètres de Smart Study", "vi": "Cài đặt Smart Study", "zh": "Smart Study 设置", "hi": "Smart Study सेटिंग्स",
    },
    "Support": {
        "de": "Unterstützung", "es": "Apoyo", "ko": "후원", "pt": "Apoio",
        "fr": "Soutien", "vi": "Ủng hộ", "zh": "支持", "hi": "समर्थन",
    },
    "Announcements, tips and updates from Smart Study.": {
        "de": "Ankündigungen, Tipps und Neuigkeiten von Smart Study.",
        "es": "Anuncios, consejos y novedades de Smart Study.",
        "ko": "Smart Study의 공지, 팁 및 업데이트입니다.",
        "pt": "Anúncios, dicas e novidades do Smart Study.",
        "fr": "Annonces, conseils et nouveautés de Smart Study.",
        "vi": "Thông báo, mẹo và cập nhật từ Smart Study.",
        "zh": "Smart Study 的公告、提示和更新。",
        "hi": "Smart Study की घोषणाएँ, सुझाव और अपडेट।",
    },
    "Known Add-on Conflict": {
        "de": "Bekannter Add-on-Konflikt", "es": "Conflicto conocido entre complementos", "ko": "알려진 애드온 충돌", "pt": "Conflito conhecido de complementos",
        "fr": "Conflit connu entre extensions", "vi": "Xung đột tiện ích bổ sung đã biết", "zh": "已知插件冲突", "hi": "ज्ञात ऐड-ऑन टकराव",
    },
    "The following add-on is known to potentially cause UI-related issues when used together with Smart Study:": {
        "de": "Das folgende Add-on kann bei gemeinsamer Verwendung mit Smart Study möglicherweise Probleme mit der Benutzeroberfläche verursachen:",
        "es": "Se sabe que el siguiente complemento puede causar problemas de interfaz al utilizarse junto con Smart Study:",
        "ko": "다음 애드온은 Smart Study와 함께 사용할 경우 UI 관련 문제를 일으킬 수 있는 것으로 알려져 있습니다:",
        "pt": "O complemento a seguir pode causar problemas de interface quando usado junto com o Smart Study:",
        "fr": "L’extension suivante est susceptible de provoquer des problèmes d’interface lorsqu’elle est utilisée avec Smart Study :",
        "vi": "Tiện ích bổ sung sau có thể gây ra sự cố giao diện khi được dùng cùng Smart Study:",
        "zh": "已知以下插件与 Smart Study 同时使用时可能导致界面相关问题：",
        "hi": "निम्न ऐड-ऑन को Smart Study के साथ उपयोग करने पर इंटरफ़ेस संबंधी समस्याएँ हो सकती हैं:",
    },
    "This may include unusual colours, layout problems or other visual glitches. If you experience these issues, please try temporarily disabling this add-on. If you need help or notice conflicts with other add-ons, contact me at github.com/TruckDrive/smart-study/issues.": {
        "de": "Dazu können ungewöhnliche Farben, Layoutprobleme oder andere Darstellungsfehler gehören. Falls solche Probleme auftreten, versuche bitte, dieses Add-on vorübergehend zu deaktivieren. Wenn du Hilfe benötigst oder Konflikte mit weiteren Add-ons bemerkst, kontaktiere mich unter github.com/TruckDrive/smart-study/issues.",
        "es": "Esto puede incluir colores inusuales, problemas de diseño u otros fallos visuales. Si experimentas estos problemas, prueba a desactivar temporalmente este complemento. Si necesitas ayuda o detectas conflictos con otros complementos, escríbeme a github.com/TruckDrive/smart-study/issues.",
        "ko": "비정상적인 색상, 레이아웃 문제 또는 기타 시각적 오류가 발생할 수 있습니다. 이러한 문제가 발생하면 이 애드온을 일시적으로 비활성화해 보세요. 도움이 필요하거나 다른 애드온과의 충돌을 발견하면 github.com/TruckDrive/smart-study/issues으로 연락해 주세요.",
        "pt": "Isso pode incluir cores incomuns, problemas de layout ou outras falhas visuais. Se esses problemas ocorrerem, tente desativar temporariamente este complemento. Se precisar de ajuda ou notar conflitos com outros complementos, entre em contato pelo e-mail github.com/TruckDrive/smart-study/issues.",
        "fr": "Cela peut inclure des couleurs inhabituelles, des problèmes de mise en page ou d’autres défauts visuels. Si vous rencontrez ces problèmes, essayez de désactiver temporairement cette extension. Si vous avez besoin d’aide ou remarquez des conflits avec d’autres extensions, contactez-moi à github.com/TruckDrive/smart-study/issues.",
        "vi": "Điều này có thể bao gồm màu sắc bất thường, lỗi bố cục hoặc các trục trặc hiển thị khác. Nếu gặp các vấn đề này, vui lòng thử tạm thời tắt tiện ích bổ sung này. Nếu bạn cần trợ giúp hoặc nhận thấy xung đột với tiện ích bổ sung khác, hãy liên hệ github.com/TruckDrive/smart-study/issues.",
        "zh": "这可能包括颜色异常、布局问题或其他视觉故障。如果遇到这些问题，请尝试暂时禁用此插件。如果需要帮助或发现与其他插件存在冲突，请通过 github.com/TruckDrive/smart-study/issues 联系我。",
        "hi": "इसमें असामान्य रंग, लेआउट समस्याएँ या अन्य दृश्य गड़बड़ियाँ शामिल हो सकती हैं। यदि ये समस्याएँ आएँ, तो कृपया इस ऐड-ऑन को अस्थायी रूप से बंद करके देखें। यदि आपको सहायता चाहिए या अन्य ऐड-ऑन के साथ टकराव दिखाई दे, तो github.com/TruckDrive/smart-study/issues पर संपर्क करें।",
    },
    "Interface language. “Auto” follows your Anki language.": {
        "de": "Oberflächensprache. „Auto“ übernimmt die Anki-Sprache.",
        "es": "Idioma de la interfaz. «Auto» usa el idioma de Anki.",
        "ko": "인터페이스 언어입니다. ‘자동’은 Anki 언어를 따릅니다.",
        "pt": "Idioma da interface. “Automático” segue o idioma do Anki.",
        "fr": "Langue de l’interface. « Auto » suit la langue d’Anki.",
        "vi": "Ngôn ngữ giao diện. “Tự động” dùng ngôn ngữ của Anki.",
        "zh": "界面语言。“自动”会跟随 Anki 的语言。",
        "hi": "इंटरफ़ेस की भाषा। “स्वतः” Anki की भाषा का उपयोग करता है।",
    },
    "Last 30 Days": {
        "de": "Letzte 30 Tage", "es": "Últimos 30 días", "ko": "최근 30일", "pt": "Últimos 30 dias",
        "fr": "30 derniers jours", "vi": "30 ngày qua", "zh": "最近 30 天", "hi": "पिछले 30 दिन",
    },
    "Source code, issues and contributions.": {
        "de": "Quellcode, Fehlermeldungen und Beiträge.", "es": "Código fuente, incidencias y contribuciones.",
        "ko": "소스 코드, 이슈 및 기여입니다.", "pt": "Código-fonte, problemas e contribuições.",
        "fr": "Code source, signalements et contributions.", "vi": "Mã nguồn, lỗi và đóng góp.",
        "zh": "源代码、问题与贡献。", "hi": "सोर्स कोड, समस्याएँ और योगदान।",
    },
    "Join": {
        "de": "Beitreten", "es": "Unirse", "ko": "참여", "pt": "Participar",
        "fr": "Rejoindre", "vi": "Tham gia", "zh": "加入", "hi": "जुड़ें",
    },
    "Enjoying Smart Study and got 5 seconds?": {
        "de": "Gefällt dir Smart Study und hast du 5 Sekunden?", "es": "¿Te gusta Smart Study y tienes 5 segundos?",
        "ko": "Smart Study가 마음에 드시나요? 5초만 내주세요!", "pt": "Gostando do Smart Study e tem 5 segundos?",
        "fr": "Smart Study vous plaît et vous avez 5 secondes ?", "vi": "Bạn thích Smart Study và có 5 giây chứ?",
        "zh": "喜欢 Smart Study，并愿意花 5 秒钟吗？", "hi": "Smart Study पसंद है और 5 सेकंड हैं?",
    },
    "Leaving a thumbs up on AnkiWeb supports development the most. Thank you so much!": {
        "de": "Ein Daumen hoch auf AnkiWeb unterstützt die Entwicklung am meisten. Vielen Dank!",
        "es": "Un voto positivo en AnkiWeb es la mejor forma de apoyar el desarrollo. ¡Muchas gracias!",
        "ko": "AnkiWeb의 추천이 개발에 가장 큰 도움이 됩니다. 정말 감사합니다!",
        "pt": "Um voto positivo no AnkiWeb é o que mais apoia o desenvolvimento. Muito obrigado!",
        "fr": "Un vote positif sur AnkiWeb est le meilleur soutien au développement. Merci beaucoup !",
        "vi": "Một lượt thích trên AnkiWeb là cách hỗ trợ phát triển tốt nhất. Cảm ơn bạn rất nhiều!",
        "zh": "在 AnkiWeb 点赞是对开发最大的支持。非常感谢！",
        "hi": "AnkiWeb पर सकारात्मक वोट विकास में सबसे अधिक मदद करता है। बहुत धन्यवाद!",
    },
    "Accent colour for buttons, highlights and widgets. Pick one to preview it live.": {
        "de": "Akzentfarbe für Schaltflächen, Hervorhebungen und Widgets. Wähle eine Farbe für die Live-Vorschau.",
        "es": "Color de acento para botones, resaltados y widgets. Elige uno para verlo al instante.",
        "ko": "버튼, 강조 표시 및 위젯의 강조 색상입니다. 선택하면 바로 미리 볼 수 있습니다.",
        "pt": "Cor de destaque para botões, realces e widgets. Escolha uma para visualizar na hora.",
        "fr": "Couleur d’accent des boutons, éléments surlignés et widgets. Choisissez-en une pour l’aperçu en direct.",
        "vi": "Màu nhấn cho nút, phần nổi bật và tiện ích. Chọn một màu để xem trước ngay.",
        "zh": "按钮、高亮和小组件所用的强调色。选择一种即可实时预览。",
        "hi": "बटन, हाइलाइट और विजेट की एक्सेंट रंग। लाइव पूर्वावलोकन के लिए एक चुनें।",
    },
    "Deck Counter Colors": {
        "de": "Farben der Deck-Zähler", "es": "Colores de los contadores de mazos", "ko": "덱 카운터 색상", "pt": "Cores dos contadores de baralho",
        "fr": "Couleurs des compteurs de paquets", "vi": "Màu bộ đếm bộ thẻ", "zh": "牌组计数器颜色", "hi": "डेक काउंटर के रंग",
    },
    "Enable Custom Counter Colors": {
        "de": "Eigene Zählerfarben aktivieren", "es": "Activar colores personalizados", "ko": "사용자 지정 카운터 색상 사용", "pt": "Ativar cores personalizadas",
        "fr": "Activer les couleurs personnalisées", "vi": "Bật màu bộ đếm tùy chỉnh", "zh": "启用自定义计数器颜色", "hi": "कस्टम काउंटर रंग चालू करें",
    },
    "Customize the New, Learn and Due numbers in the main Deck Browser.": {
        "de": "Passe die Farben der Zahlen für Neu, Lernen und Fällig im Haupt-Deckbrowser an.",
        "es": "Personaliza los números Nuevas, Aprender y Pendientes del explorador principal de mazos.",
        "ko": "기본 덱 브라우저의 새 카드, 학습 및 복습 예정 숫자 색상을 설정합니다.",
        "pt": "Personalize os números Novos, Aprender e Pendentes no navegador principal de baralhos.",
        "fr": "Personnalisez les nombres Nouvelles, Apprentissage et À réviser dans le navigateur principal de paquets.",
        "vi": "Tùy chỉnh màu số Thẻ mới, Đang học và Đến hạn trong trình duyệt bộ thẻ chính.",
        "zh": "自定义主牌组浏览器中新卡、学习和到期数量的颜色。",
        "hi": "मुख्य डेक ब्राउज़र में नए, सीखने और देय कार्डों की संख्याओं के रंग बदलें।",
    },
    "Light Mode Colors": {
        "de": "Farben im hellen Modus", "es": "Colores del modo claro", "ko": "라이트 모드 색상", "pt": "Cores do modo claro",
        "fr": "Couleurs du mode clair", "vi": "Màu chế độ sáng", "zh": "浅色模式颜色", "hi": "लाइट मोड के रंग",
    },
    "Dark Mode Colors": {
        "de": "Farben im dunklen Modus", "es": "Colores del modo oscuro", "ko": "다크 모드 색상", "pt": "Cores do modo escuro",
        "fr": "Couleurs du mode sombre", "vi": "Màu chế độ tối", "zh": "深色模式颜色", "hi": "डार्क मोड के रंग",
    },
    "Due": {
        "de": "Fällig", "es": "Pendientes", "ko": "복습 예정", "pt": "Pendentes",
        "fr": "À réviser", "vi": "Đến hạn", "zh": "到期", "hi": "देय",
    },
    "Only affects the card counters in the main Deck Browser.": {
        "de": "Wirkt sich nur auf die Kartenzähler im Haupt-Deckbrowser aus.",
        "es": "Solo afecta a los contadores de tarjetas del explorador principal de mazos.",
        "ko": "기본 덱 브라우저의 카드 카운터에만 적용됩니다.",
        "pt": "Afeta apenas os contadores de cartões no navegador principal de baralhos.",
        "fr": "Affecte uniquement les compteurs de cartes du navigateur principal de paquets.",
        "vi": "Chỉ ảnh hưởng đến bộ đếm thẻ trong trình duyệt bộ thẻ chính.",
        "zh": "仅影响主牌组浏览器中的卡片计数器。",
        "hi": "केवल मुख्य डेक ब्राउज़र के कार्ड काउंटरों पर लागू होता है।",
    },
    "Restore Counter Defaults": {
        "de": "Standardfarben wiederherstellen", "es": "Restaurar colores predeterminados", "ko": "기본 카운터 색상 복원", "pt": "Restaurar cores padrão",
        "fr": "Restaurer les couleurs par défaut", "vi": "Khôi phục màu mặc định", "zh": "恢复默认计数器颜色", "hi": "डिफ़ॉल्ट काउंटर रंग बहाल करें",
    },
    "Edit Theme ✎": {
        "de": "Theme bearbeiten ✎", "es": "Editar tema ✎", "ko": "테마 편집 ✎", "pt": "Editar tema ✎",
        "fr": "Modifier le thème ✎", "vi": "Chỉnh sửa chủ đề ✎", "zh": "编辑主题 ✎", "hi": "थीम संपादित करें ✎",
    },
    "Background": {
        "de": "Hintergrund", "es": "Fondo", "ko": "배경", "pt": "Fundo",
        "fr": "Arrière-plan", "vi": "Nền", "zh": "背景", "hi": "पृष्ठभूमि",
    },
    "What changed in recent versions of Smart Study.": {
        "de": "Änderungen in den letzten Smart Study-Versionen.", "es": "Cambios en las últimas versiones de Smart Study.",
        "ko": "최근 Smart Study 버전의 변경 사항입니다.", "pt": "O que mudou nas versões recentes do Smart Study.",
        "fr": "Les changements des versions récentes de Smart Study.", "vi": "Những thay đổi trong các phiên bản Smart Study gần đây.",
        "zh": "Smart Study 最近版本的更新内容。", "hi": "Smart Study के हाल के संस्करणों में हुए बदलाव।",
    },
    "The people who help keep Smart Study going.": {
        "de": "Die Menschen, die Smart Study am Laufen halten.", "es": "Las personas que ayudan a mantener Smart Study.",
        "ko": "Smart Study가 계속될 수 있도록 돕는 분들입니다.", "pt": "As pessoas que ajudam o Smart Study a continuar.",
        "fr": "Les personnes qui aident Smart Study à continuer.", "vi": "Những người giúp Smart Study tiếp tục phát triển.",
        "zh": "帮助 Smart Study 持续发展的支持者。", "hi": "वे लोग जो Smart Study को आगे बढ़ने में मदद करते हैं।",
    },
    "Custom Deck Dashboard": {
        "de": "Benutzerdefinierte Deck-Übersicht", "es": "Panel de mazo personalizado", "ko": "사용자 지정 덱 대시보드", "pt": "Painel personalizado do baralho",
        "fr": "Tableau de bord personnalisé du paquet", "vi": "Bảng điều khiển bộ thẻ tùy chỉnh", "zh": "自定义牌组面板", "hi": "कस्टम डेक डैशबोर्ड",
    },
    "Minimalist Dashboard": {
        "de": "Minimalistisches Dashboard", "es": "Panel minimalista", "ko": "미니멀 대시보드", "pt": "Painel minimalista",
        "fr": "Tableau de bord minimaliste", "vi": "Bảng điều khiển tối giản", "zh": "极简仪表板", "hi": "मिनिमल डैशबोर्ड",
    },
    "Shows level, streak, challenge, study plan, deadline and key statistics in one compact panel.": {
        "de": "Zeigt Level, Streak, Challenge, Lernplan, Deadline und die wichtigsten Statistiken in einem kompakten Panel.",
        "es": "Muestra el nivel, la racha, el reto, el plan de estudio, la fecha límite y las estadísticas clave en un panel compacto.",
        "ko": "레벨, 스트릭, 챌린지, 학습 계획, 마감일과 핵심 통계를 하나의 간결한 패널에 표시합니다.",
        "pt": "Mostra nível, sequência, desafio, plano de estudos, prazo e estatísticas principais em um painel compacto.",
        "fr": "Affiche le niveau, la série, le défi, le plan d’étude, l’échéance et les statistiques clés dans un panneau compact.",
        "vi": "Hiển thị cấp độ, chuỗi ngày, thử thách, kế hoạch học, thời hạn và thống kê chính trong một bảng gọn.",
        "zh": "在一个紧凑面板中显示等级、连续学习、挑战、学习计划、截止日期和关键统计。",
        "hi": "स्तर, स्ट्रीक, चुनौती, अध्ययन योजना, समयसीमा और मुख्य आँकड़े एक कॉम्पैक्ट पैनल में दिखाता है।",
    },
    "Individual dashboard widgets are unavailable while Minimalist Dashboard is enabled.": {
        "de": "Die einzelnen Dashboard-Widgets sind nicht verfügbar, solange das minimalistische Dashboard aktiviert ist.",
        "es": "Los widgets individuales no están disponibles mientras el panel minimalista está activado.",
        "ko": "미니멀 대시보드가 활성화된 동안 개별 대시보드 위젯을 사용할 수 없습니다.",
        "pt": "Os widgets individuais ficam indisponíveis enquanto o painel minimalista estiver ativado.",
        "fr": "Les widgets individuels sont indisponibles tant que le tableau de bord minimaliste est activé.",
        "vi": "Các widget riêng lẻ không khả dụng khi bảng điều khiển tối giản đang bật.",
        "zh": "启用极简仪表板时，无法使用单独的仪表板小组件。",
        "hi": "मिनिमल डैशबोर्ड चालू रहने पर अलग-अलग डैशबोर्ड विजेट उपलब्ध नहीं होते।",
    },
    "Replaces the standard overview with retention, hard cards and more.": {
        "de": "Ersetzt die Standardübersicht durch Retention, schwierige Karten und mehr.",
        "es": "Sustituye el resumen estándar por retención, tarjetas difíciles y más.",
        "ko": "기본 개요를 기억 유지율, 어려운 카드 등의 정보로 대체합니다.",
        "pt": "Substitui a visão padrão por retenção, cartões difíceis e muito mais.",
        "fr": "Remplace l’aperçu standard par la rétention, les cartes difficiles et plus encore.",
        "vi": "Thay phần tổng quan mặc định bằng tỷ lệ ghi nhớ, thẻ khó và nhiều thông tin khác.",
        "zh": "用记忆保持率、困难卡片等内容替换标准概览。",
        "hi": "मानक ओवरव्यू को रिटेंशन, कठिन कार्ड और अन्य जानकारी से बदलता है।",
    },
    "Set keyboard shortcut": {
        "de": "Tastenkürzel festlegen", "es": "Asignar atajo de teclado", "ko": "키보드 단축키 설정", "pt": "Definir atalho de teclado",
        "fr": "Définir le raccourci clavier", "vi": "Đặt phím tắt", "zh": "设置键盘快捷键", "hi": "कीबोर्ड शॉर्टकट सेट करें",
    },
    "Add Shortcut": {
        "de": "Kürzel hinzufügen", "es": "Añadir atajo", "ko": "단축키 추가", "pt": "Adicionar atalho",
        "fr": "Ajouter un raccourci", "vi": "Thêm phím tắt", "zh": "添加快捷键", "hi": "शॉर्टकट जोड़ें",
    },
    "No changelog yet": {
        "de": "Noch kein Änderungsprotokoll", "es": "Aún no hay registro de cambios", "ko": "아직 변경 기록이 없습니다", "pt": "Ainda não há histórico de alterações",
        "fr": "Aucun journal des modifications pour le moment", "vi": "Chưa có nhật ký thay đổi", "zh": "暂无更新日志", "hi": "अभी कोई बदलाव सूची नहीं है",
    },
    "Supporters will be listed here soon": {
        "de": "Unterstützende werden hier bald aufgeführt", "es": "Pronto aparecerán aquí las personas que apoyan el proyecto", "ko": "후원자 목록이 곧 여기에 표시됩니다", "pt": "Os apoiadores serão listados aqui em breve",
        "fr": "Les soutiens seront bientôt affichés ici", "vi": "Những người ủng hộ sẽ sớm được liệt kê tại đây", "zh": "支持者名单即将在此显示", "hi": "समर्थकों की सूची जल्द यहाँ दिखाई जाएगी",
    },
    "A heartfelt thank you to everyone who supports Smart Study. This space is reserved for you.": {
        "de": "Herzlichen Dank an alle, die Smart Study unterstützen. Dieser Platz ist für euch reserviert.",
        "es": "Gracias de corazón a quienes apoyan Smart Study. Este espacio está reservado para vosotros.",
        "ko": "Smart Study를 후원해 주시는 모든 분께 진심으로 감사드립니다. 이 공간은 여러분을 위한 곳입니다.",
        "pt": "Um agradecimento de coração a todos que apoiam o Smart Study. Este espaço é de vocês.",
        "fr": "Un immense merci à toutes les personnes qui soutiennent Smart Study. Cet espace vous est réservé.",
        "vi": "Chân thành cảm ơn tất cả những ai ủng hộ Smart Study. Không gian này dành cho các bạn.",
        "zh": "衷心感谢每一位支持 Smart Study 的人。这个位置为你们而留。",
        "hi": "Smart Study का समर्थन करने वाले सभी लोगों को दिल से धन्यवाद। यह स्थान आपके लिए है।",
    },
    "Smart Study error": {
        "de": "Smart Study-Fehler", "es": "Error de Smart Study", "ko": "Smart Study 오류", "pt": "Erro do Smart Study",
        "fr": "Erreur Smart Study", "vi": "Lỗi Smart Study", "zh": "Smart Study 错误", "hi": "Smart Study त्रुटि",
    },
    "Show details": {
        "de": "Details anzeigen", "es": "Mostrar detalles", "ko": "세부 정보 보기", "pt": "Mostrar detalhes",
        "fr": "Afficher les détails", "vi": "Hiện chi tiết", "zh": "显示详情", "hi": "विवरण दिखाएँ",
    },
    "Hide details": {
        "de": "Details ausblenden", "es": "Ocultar detalles", "ko": "세부 정보 숨기기", "pt": "Ocultar detalhes",
        "fr": "Masquer les détails", "vi": "Ẩn chi tiết", "zh": "隐藏详情", "hi": "विवरण छिपाएँ",
    },
    "Copy error": {
        "de": "Fehler kopieren", "es": "Copiar error", "ko": "오류 복사", "pt": "Copiar erro",
        "fr": "Copier l’erreur", "vi": "Sao chép lỗi", "zh": "复制错误", "hi": "त्रुटि कॉपी करें",
    },
    "Copied!": {
        "de": "Kopiert!", "es": "¡Copiado!", "ko": "복사됨!", "pt": "Copiado!",
        "fr": "Copié !", "vi": "Đã sao chép!", "zh": "已复制！", "hi": "कॉपी हो गया!",
    },
    "Dismiss": {
        "de": "Schließen", "es": "Cerrar", "ko": "닫기", "pt": "Fechar",
        "fr": "Fermer", "vi": "Đóng", "zh": "关闭", "hi": "बंद करें",
    },
    "Unexpected error": {
        "de": "Unerwarteter Fehler", "es": "Error inesperado", "ko": "예기치 않은 오류", "pt": "Erro inesperado",
        "fr": "Erreur inattendue", "vi": "Lỗi không mong đợi", "zh": "意外错误", "hi": "अप्रत्याशित त्रुटि",
    },
    "Unexpected error (async)": {
        "de": "Unerwarteter Fehler (asynchron)", "es": "Error inesperado (asíncrono)", "ko": "예기치 않은 오류(비동기)", "pt": "Erro inesperado (assíncrono)",
        "fr": "Erreur inattendue (asynchrone)", "vi": "Lỗi không mong đợi (bất đồng bộ)", "zh": "意外错误（异步）", "hi": "अप्रत्याशित त्रुटि (असिंक्रोनस)",
    },
    "Your data is safe. Please screenshot the details and send them to github.com/TruckDrive/smart-study/issues.": {
        "de": "Deine Daten sind sicher. Bitte erstelle einen Screenshot der Details und sende ihn an github.com/TruckDrive/smart-study/issues.",
        "es": "Tus datos están seguros. Haz una captura de los detalles y envíala a github.com/TruckDrive/smart-study/issues.",
        "ko": "데이터는 안전합니다. 세부 정보의 스크린샷을 찍어 github.com/TruckDrive/smart-study/issues으로 보내 주세요.",
        "pt": "Seus dados estão seguros. Tire uma captura dos detalhes e envie para github.com/TruckDrive/smart-study/issues.",
        "fr": "Vos données sont en sécurité. Faites une capture des détails et envoyez-la à github.com/TruckDrive/smart-study/issues.",
        "vi": "Dữ liệu của bạn vẫn an toàn. Hãy chụp phần chi tiết và gửi đến github.com/TruckDrive/smart-study/issues.",
        "zh": "你的数据是安全的。请截取详情并发送至 github.com/TruckDrive/smart-study/issues。",
        "hi": "आपका डेटा सुरक्षित है। कृपया विवरण का स्क्रीनशॉट लेकर github.com/TruckDrive/smart-study/issues पर भेजें।",
    },
    "(no stack trace available)": {
        "de": "(kein Stacktrace verfügbar)", "es": "(no hay traza disponible)", "ko": "(스택 추적 없음)", "pt": "(rastreamento de pilha indisponível)",
        "fr": "(aucune trace disponible)", "vi": "(không có dấu vết ngăn xếp)", "zh": "（无可用堆栈跟踪）", "hi": "(स्टैक ट्रेस उपलब्ध नहीं है)",
    },
    "July 2026": {
        "de": "Juli 2026", "es": "julio de 2026", "ko": "2026년 7월", "pt": "julho de 2026",
        "fr": "juillet 2026", "vi": "tháng 7 năm 2026", "zh": "2026 年 7 月", "hi": "जुलाई 2026",
    },
    "May 2026": {
        "de": "Mai 2026", "es": "mayo de 2026", "ko": "2026년 5월", "pt": "maio de 2026",
        "fr": "mai 2026", "vi": "tháng 5 năm 2026", "zh": "2026 年 5 月", "hi": "मई 2026",
    },
    "New: redesigned Settings with a cleaner, category-based layout.": {
        "de": "Neu: überarbeitete Einstellungen mit übersichtlicher, kategoriebasierter Struktur.",
        "es": "Novedad: ajustes rediseñados con una estructura más clara por categorías.",
        "ko": "신규: 더 깔끔한 카테고리 기반 구성으로 설정 화면을 새롭게 디자인했습니다.",
        "pt": "Novo: configurações redesenhadas com uma estrutura mais limpa por categorias.",
        "fr": "Nouveau : paramètres repensés avec une présentation plus claire par catégories.",
        "vi": "Mới: thiết kế lại phần Cài đặt với bố cục theo danh mục rõ ràng hơn.",
        "zh": "新增：重新设计设置界面，采用更清晰的分类布局。",
        "hi": "नया: अधिक साफ़, श्रेणी-आधारित लेआउट के साथ सेटिंग्स को नया रूप दिया गया।",
    },
    "Notebook: insert a line between any two lines, cover/hide terms for self-testing, link to other pages, and many more icons.": {
        "de": "Notizbuch: Zeilen zwischen vorhandenen Zeilen einfügen, Begriffe zum Selbsttest abdecken, andere Seiten verlinken und viele weitere Symbole nutzen.",
        "es": "Cuaderno: inserta líneas entre otras, cubre términos para autoevaluarte, enlaza otras páginas y usa muchos más iconos.",
        "ko": "노트북: 줄 사이에 새 줄을 삽입하고, 자가 테스트용 용어 가리기, 다른 페이지 연결 및 다양한 아이콘을 사용할 수 있습니다.",
        "pt": "Caderno: insira linhas entre outras, cubra termos para autoavaliação, vincule outras páginas e use muitos outros ícones.",
        "fr": "Carnet : insérez une ligne entre deux lignes, masquez des termes pour vous tester, liez d’autres pages et profitez de nombreuses icônes.",
        "vi": "Sổ tay: chèn dòng giữa hai dòng, che thuật ngữ để tự kiểm tra, liên kết trang khác và dùng thêm nhiều biểu tượng.",
        "zh": "笔记本：可在任意两行之间插入新行、遮盖术语进行自测、链接其他页面，并新增更多图标。",
        "hi": "नोटबुक: किसी भी दो पंक्तियों के बीच पंक्ति जोड़ें, स्वयं-जाँच के लिए शब्द छिपाएँ, अन्य पृष्ठ लिंक करें और अधिक आइकन उपयोग करें।",
    },
    "AI Assistant: updated to current Gemini models and fixed the Quick Action buttons not enabling.": {
        "de": "KI-Assistent: aktuelle Gemini-Modelle ergänzt und die Aktivierung der Schnellaktions-Schaltflächen korrigiert.",
        "es": "Asistente de IA: actualizado a los modelos Gemini actuales y corregida la activación de las acciones rápidas.",
        "ko": "AI 어시스턴트: 최신 Gemini 모델로 업데이트하고 빠른 작업 버튼이 활성화되지 않던 문제를 수정했습니다.",
        "pt": "Assistente de IA: atualizado para os modelos Gemini atuais e corrigida a ativação dos botões de ação rápida.",
        "fr": "Assistant IA : mise à jour vers les modèles Gemini actuels et correction de l’activation des actions rapides.",
        "vi": "Trợ lý AI: cập nhật các mô hình Gemini hiện tại và sửa lỗi nút Tác vụ nhanh không được bật.",
        "zh": "AI 助手：更新至当前 Gemini 模型，并修复快捷操作按钮无法启用的问题。",
        "hi": "AI सहायक: मौजूदा Gemini मॉडल अपडेट किए और क्विक एक्शन बटन सक्रिय न होने की समस्या ठीक की।",
    },
    "Study Plan: mark a subject as done early, a 'time is up' notification that also shows while reviewing, and a cleaner timer popup.": {
        "de": "Lernplan: Fächer vorzeitig als erledigt markieren, eine auch beim Wiederholen sichtbare Zeitablauf-Meldung und ein aufgeräumteres Timer-Fenster.",
        "es": "Plan de estudio: marca asignaturas como terminadas antes, recibe el aviso de tiempo incluso al repasar y usa un temporizador más claro.",
        "ko": "학습 계획: 과목을 일찍 완료 처리하고, 복습 중에도 시간 종료 알림을 받으며, 더 깔끔한 타이머 팝업을 사용할 수 있습니다.",
        "pt": "Plano de estudo: conclua uma matéria antecipadamente, receba o aviso de tempo durante revisões e use um pop-up de timer mais limpo.",
        "fr": "Programme d’étude : terminez une matière en avance, recevez l’alerte de fin même pendant les révisions et profitez d’un minuteur plus clair.",
        "vi": "Kế hoạch học: đánh dấu môn hoàn thành sớm, nhận thông báo hết giờ cả khi ôn thẻ và dùng cửa sổ hẹn giờ gọn hơn.",
        "zh": "学习计划：可提前将科目标记为完成；计时结束通知也会在复习时显示；计时器弹窗更加简洁。",
        "hi": "अध्ययन योजना: विषय को पहले पूरा चिह्नित करें, समीक्षा के दौरान भी समय पूरा होने की सूचना पाएँ और साफ़ टाइमर पॉपअप उपयोग करें।",
    },
    "Release hardening: profile-isolated browser data, local API-key storage, safer HTML/PDF handling, and consistent Anki-day calculations.": {
        "de": "Release-Härtung: profilgetrennte Browserdaten, lokale API-Schlüssel, sicherere HTML-/PDF-Verarbeitung und einheitliche Anki-Tagesberechnung.",
        "es": "Refuerzo de la versión: datos del navegador separados por perfil, claves API locales, HTML/PDF más seguros y cálculo coherente del día de Anki.",
        "ko": "릴리스 강화: 프로필별 브라우저 데이터, 로컬 API 키 저장, 더 안전한 HTML/PDF 처리 및 일관된 Anki 날짜 계산.",
        "pt": "Reforço da versão: dados do navegador separados por perfil, chaves de API locais, HTML/PDF mais seguros e cálculo consistente do dia do Anki.",
        "fr": "Renforcement de la version : données du navigateur isolées par profil, clés API locales, traitement HTML/PDF plus sûr et calcul cohérent du jour Anki.",
        "vi": "Gia cố bản phát hành: dữ liệu trình duyệt tách theo hồ sơ, khóa API lưu cục bộ, xử lý HTML/PDF an toàn hơn và tính ngày Anki nhất quán.",
        "zh": "版本加固：浏览器数据按配置文件隔离、API 密钥本地存储、更安全的 HTML/PDF 处理，以及一致的 Anki 日界计算。",
        "hi": "रिलीज़ सुरक्षा: प्रोफ़ाइल-पृथक ब्राउज़र डेटा, स्थानीय API-कुंजी संग्रह, सुरक्षित HTML/PDF प्रबंधन और सुसंगत Anki-दिन गणना।",
    },
    "Added the AI Assistant sidebar.": {
        "de": "KI-Assistent-Seitenleiste hinzugefügt.", "es": "Añadida la barra lateral del asistente de IA.",
        "ko": "AI 어시스턴트 사이드바를 추가했습니다.", "pt": "Adicionada a barra lateral do Assistente de IA.",
        "fr": "Ajout de la barre latérale de l’assistant IA.", "vi": "Đã thêm thanh bên Trợ lý AI.",
        "zh": "新增 AI 助手侧边栏。", "hi": "AI सहायक साइडबार जोड़ा गया।",
    },
    "Performance and stability improvements across the add-on.": {
        "de": "Leistungs- und Stabilitätsverbesserungen im gesamten Add-on.", "es": "Mejoras de rendimiento y estabilidad en todo el complemento.",
        "ko": "애드온 전반의 성능과 안정성을 개선했습니다.", "pt": "Melhorias de desempenho e estabilidade em todo o add-on.",
        "fr": "Améliorations des performances et de la stabilité dans tout l’add-on.", "vi": "Cải thiện hiệu năng và độ ổn định trên toàn tiện ích.",
        "zh": "全面提升插件的性能与稳定性。", "hi": "पूरे ऐड-ऑन में प्रदर्शन और स्थिरता सुधार।",
    },
}


_LANGS = ("de", "es", "ko", "pt", "fr", "vi", "zh", "hi")


def _add_rows(rows):
    for row in rows:
        WEB_TRANSLATIONS[row[0]] = dict(zip(_LANGS, row[1:]))


# AI Assistant: interface, status text, context controls and button manager.
_add_rows([
    ("Custom Background", "Eigener Hintergrund", "Fondo personalizado", "사용자 배경", "Fundo personalizado", "Arrière-plan personnalisé", "Nền tùy chỉnh", "自定义背景", "कस्टम पृष्ठभूमि"),
    ("Enable Custom Background", "Eigenen Hintergrund aktivieren", "Activar fondo personalizado", "사용자 배경 활성화", "Ativar fundo personalizado", "Activer l’arrière-plan personnalisé", "Bật nền tùy chỉnh", "启用自定义背景", "कस्टम पृष्ठभूमि चालू करें"),
    ("Show one optimized image across the dashboard and toolbars.", "Ein optimiertes Bild durchgehend im Dashboard und in den Toolbars anzeigen.", "Muestra una imagen optimizada en el panel y las barras de herramientas.", "최적화된 이미지 하나를 대시보드와 도구 모음 전체에 표시합니다.", "Mostra uma imagem otimizada no painel e nas barras de ferramentas.", "Affiche une image optimisée sur le tableau de bord et les barres d’outils.", "Hiển thị một ảnh đã tối ưu trên bảng điều khiển và thanh công cụ.", "在仪表板和工具栏中连续显示一张优化图片。", "डैशबोर्ड और टूलबार में एक अनुकूलित चित्र दिखाएँ।"),
    ("No background image selected.", "Kein Hintergrundbild ausgewählt.", "No se ha seleccionado ninguna imagen de fondo.", "선택한 배경 이미지가 없습니다.", "Nenhuma imagem de fundo selecionada.", "Aucune image d’arrière-plan sélectionnée.", "Chưa chọn ảnh nền.", "尚未选择背景图片。", "कोई पृष्ठभूमि चित्र नहीं चुना गया।"),
    ("Choose Image", "Bild auswählen", "Elegir imagen", "이미지 선택", "Escolher imagem", "Choisir une image", "Chọn ảnh", "选择图片", "चित्र चुनें"),
    ("Remove", "Entfernen", "Eliminar", "제거", "Remover", "Supprimer", "Xóa", "移除", "हटाएँ"),
    ("PNG, JPEG or WebP · maximum 20 MB and 40 megapixels. Large valid images are optimized automatically.", "PNG, JPEG oder WebP · maximal 20 MB und 40 Megapixel. Große gültige Bilder werden automatisch optimiert.", "PNG, JPEG o WebP · máximo 20 MB y 40 megapíxeles. Las imágenes grandes válidas se optimizan automáticamente.", "PNG, JPEG 또는 WebP · 최대 20MB 및 4천만 화소. 유효한 큰 이미지는 자동으로 최적화됩니다.", "PNG, JPEG ou WebP · máximo de 20 MB e 40 megapixels. Imagens grandes válidas são otimizadas automaticamente.", "PNG, JPEG ou WebP · 20 Mo et 40 mégapixels maximum. Les grandes images valides sont optimisées automatiquement.", "PNG, JPEG hoặc WebP · tối đa 20 MB và 40 megapixel. Ảnh lớn hợp lệ được tự động tối ưu.", "PNG、JPEG 或 WebP · 最大 20 MB 和 4000 万像素。有效的大图会自动优化。", "PNG, JPEG या WebP · अधिकतम 20 MB और 40 मेगापिक्सेल। बड़े मान्य चित्र अपने आप अनुकूलित किए जाते हैं।"),
    ("Blur", "Unschärfe", "Desenfoque", "흐림", "Desfoque", "Flou", "Độ mờ", "模糊", "धुंधलापन"),
    ("Applied once and cached for smooth performance.", "Wird einmal angewendet und für eine flüssige Darstellung zwischengespeichert.", "Se aplica una vez y se guarda en caché para un rendimiento fluido.", "한 번 적용한 뒤 부드러운 성능을 위해 캐시됩니다.", "Aplicado uma vez e armazenado em cache para desempenho fluido.", "Appliqué une fois puis mis en cache pour des performances fluides.", "Chỉ áp dụng một lần và được lưu đệm để hoạt động mượt mà.", "仅应用一次并缓存，以确保流畅性能。", "एक बार लागू करके सुचारु प्रदर्शन के लिए कैश किया जाता है।"),
    ("Dark Overlay", "Dunkles Overlay", "Capa oscura", "어두운 오버레이", "Sobreposição escura", "Voile sombre", "Lớp phủ tối", "深色遮罩", "गहरा ओवरले"),
    ("Darkens the image to improve readability.", "Dunkelt das Bild ab, um die Lesbarkeit zu verbessern.", "Oscurece la imagen para mejorar la legibilidad.", "가독성을 높이기 위해 이미지를 어둡게 합니다.", "Escurece a imagem para melhorar a legibilidade.", "Assombrit l’image pour améliorer la lisibilité.", "Làm tối ảnh để dễ đọc hơn.", "调暗图片以提高可读性。", "पढ़ने में आसानी के लिए चित्र को गहरा करता है।"),
    ("Studied Text", "Studiert-Text", "Texto de estudio", "학습 요약 텍스트", "Texto de estudo", "Texte du résumé", "Văn bản đã học", "学习摘要文字", "अध्ययन सारांश टेक्स्ट"),
    ("Choose a light or dark colour for the studied-today summary.", "Eine helle oder dunkle Farbe für die heutige Lernzusammenfassung wählen.", "Elige un color claro u oscuro para el resumen de estudio de hoy.", "오늘의 학습 요약에 밝거나 어두운 색상을 선택합니다.", "Escolha uma cor clara ou escura para o resumo de estudo de hoje.", "Choisissez une couleur claire ou sombre pour le résumé d’étude du jour.", "Chọn màu sáng hoặc tối cho phần tóm tắt học hôm nay.", "为今日学习摘要选择浅色或深色。", "आज के अध्ययन सारांश के लिए हल्का या गहरा रंग चुनें।"),
    ("Dark", "Dunkel", "Oscuro", "어둡게", "Escuro", "Sombre", "Tối", "深色", "गहरा"),
    ("Light", "Hell", "Claro", "밝게", "Claro", "Clair", "Sáng", "浅色", "हल्का"),
    ("Image Position", "Bildposition", "Posición de la imagen", "이미지 위치", "Posição da imagem", "Position de l’image", "Vị trí ảnh", "图片位置", "चित्र की स्थिति"),
    ("Choose which part of the image stays visible when it is cropped.", "Auswählen, welcher Bildbereich beim Zuschneiden sichtbar bleibt.", "Elige qué parte de la imagen permanece visible al recortarla.", "이미지가 잘릴 때 계속 보일 부분을 선택합니다.", "Escolha qual parte da imagem permanece visível ao recortá-la.", "Choisissez la partie de l’image qui reste visible lors du recadrage.", "Chọn phần ảnh vẫn hiển thị khi ảnh bị cắt.", "选择裁剪时要保留可见的图片区域。", "क्रॉप होने पर चित्र का कौन-सा भाग दिखाई दे, यह चुनें।"),
    ("Top", "Oben", "Arriba", "위", "Topo", "Haut", "Trên", "顶部", "ऊपर"),
    ("Center", "Mitte", "Centro", "가운데", "Centro", "Centre", "Giữa", "居中", "मध्य"),
    ("Bottom", "Unten", "Abajo", "아래", "Inferior", "Bas", "Dưới", "底部", "नीचे"),
    ("Restore Defaults", "Standardeinstellungen wiederherstellen", "Restaurar valores predeterminados", "기본값 복원", "Restaurar padrões", "Rétablir les réglages par défaut", "Khôi phục mặc định", "恢复默认设置", "डिफ़ॉल्ट पुनर्स्थापित करें"),
    ("This image must be enlarged considerably to fill the current window and may appear soft.", "Dieses Bild muss stark vergrößert werden, um das aktuelle Fenster auszufüllen, und könnte dadurch unscharf wirken.", "Esta imagen debe ampliarse considerablemente para llenar la ventana actual y puede verse borrosa.", "현재 창을 채우려면 이 이미지를 크게 확대해야 하므로 흐릿하게 보일 수 있습니다.", "Esta imagem precisa ser ampliada consideravelmente para preencher a janela atual e pode parecer desfocada.", "Cette image doit être fortement agrandie pour remplir la fenêtre actuelle et risque de paraître floue.", "Ảnh này phải được phóng to đáng kể để lấp đầy cửa sổ hiện tại và có thể trông mờ.", "此图片需要大幅放大才能填满当前窗口，因此可能显得模糊。", "वर्तमान विंडो भरने के लिए इस चित्र को काफी बड़ा करना होगा, इसलिए यह धुंधला दिख सकता है।"),
    ("English", "Englisch", "Inglés", "영어", "Inglês", "Anglais", "Tiếng Anh", "英语", "अंग्रेज़ी"),
    ("Japanese", "Japanisch", "Japonés", "일본어", "Japonês", "Japonais", "Tiếng Nhật", "日语", "जापानी"),
    ("Korean", "Koreanisch", "Coreano", "한국어", "Coreano", "Coréen", "Tiếng Hàn", "韩语", "कोरियाई"),
    ("Save", "Speichern", "Guardar", "저장", "Salvar", "Enregistrer", "Lưu", "保存", "सेव करें"),
    ("Quick Action Buttons", "Schnellaktions-Schaltflächen", "Botones de acción rápida", "빠른 작업 버튼", "Botões de ação rápida", "Boutons d’action rapide", "Nút tác vụ nhanh", "快捷操作按钮", "क्विक एक्शन बटन"),
    ("Built-in", "Integriert", "Integrados", "기본 제공", "Integrados", "Intégrés", "Tích hợp sẵn", "内置", "अंतर्निहित"),
    ("On", "An", "Activado", "켜짐", "Ligado", "Activé", "Bật", "开", "चालू"),
    ("Off", "Aus", "Desactivado", "꺼짐", "Desligado", "Désactivé", "Tắt", "关", "बंद"),
])

# AI Assistant: explanatory text and provider-specific key setup guides.
_add_rows([
])


# Notebook, page links and the PDF library's dynamic messages.
_add_rows([
    ("Page Title", "Seitentitel", "Título de la página", "페이지 제목", "Título da página", "Titre de la page", "Tiêu đề trang", "页面标题", "पृष्ठ शीर्षक"),
    ("Search or create a page…", "Seite suchen oder erstellen …", "Buscar o crear una página…", "페이지 검색 또는 만들기…", "Pesquisar ou criar uma página…", "Rechercher ou créer une page…", "Tìm hoặc tạo trang…", "搜索或创建页面…", "पृष्ठ खोजें या बनाएँ…"),
    ("Remove cover", "Abdeckung entfernen", "Quitar cubierta", "가리개 제거", "Remover cobertura", "Retirer le masque", "Bỏ phần che", "移除遮盖", "कवर हटाएँ"),
    ('New page: "{title}"', 'Neue Seite: „{title}“', 'Nueva página: «{title}»', '새 페이지: “{title}”', 'Nova página: “{title}”', 'Nouvelle page : « {title} »', 'Trang mới: “{title}”', '新页面：“{title}”', 'नया पृष्ठ: “{title}”'),
    ("Create new page", "Neue Seite erstellen", "Crear una página", "새 페이지 만들기", "Criar nova página", "Créer une page", "Tạo trang mới", "创建新页面", "नया पृष्ठ बनाएँ"),
    ("Page not found", "Seite nicht gefunden", "Página no encontrada", "페이지를 찾을 수 없음", "Página não encontrada", "Page introuvable", "Không tìm thấy trang", "找不到页面", "पृष्ठ नहीं मिला"),
    ("Link (Ctrl+K)", "Link (Strg+K)", "Enlace (Ctrl+K)", "링크(Ctrl+K)", "Link (Ctrl+K)", "Lien (Ctrl+K)", "Liên kết (Ctrl+K)", "链接（Ctrl+K）", "लिंक (Ctrl+K)"),
    ("Cover for learning", "Zum Lernen abdecken", "Cubrir para estudiar", "학습용으로 가리기", "Cobrir para estudar", "Masquer pour réviser", "Che để học", "遮盖以便学习", "सीखने के लिए ढकें"),
    ("Cover all revealed terms again", "Alle aufgedeckten Begriffe wieder abdecken", "Volver a cubrir todos los términos revelados", "드러난 모든 용어 다시 가리기", "Cobrir novamente todos os termos revelados", "Masquer à nouveau tous les termes révélés", "Che lại mọi thuật ngữ đã mở", "重新遮盖所有已显示术语", "सभी खोले गए शब्द फिर ढकें"),
    ("Link to page", "Seite verlinken", "Enlazar a una página", "페이지에 연결", "Vincular a uma página", "Lier à une page", "Liên kết đến trang", "链接到页面", "पृष्ठ से लिंक करें"),
    ("Unfiled", "Nicht zugeordnet", "Sin archivar", "미분류", "Sem pasta", "Non classés", "Chưa phân loại", "未归档", "अवर्गीकृत"),
    ("No folders yet.", "Noch keine Ordner.", "Aún no hay carpetas.", "아직 폴더가 없습니다.", "Ainda não há pastas.", "Aucun dossier pour le moment.", "Chưa có thư mục.", "还没有文件夹。", "अभी कोई फ़ोल्डर नहीं।"),
    ('No PDFs in "{folder}" yet.', 'Noch keine PDFs in „{folder}“.', 'Aún no hay PDF en «{folder}».', '“{folder}”에 아직 PDF가 없습니다.', 'Ainda não há PDFs em “{folder}”.', 'Aucun PDF dans « {folder} » pour le moment.', 'Chưa có PDF trong “{folder}”.', '“{folder}”中还没有 PDF。', '“{folder}” में अभी कोई PDF नहीं है।'),
    ("File missing", "Datei fehlt", "Falta el archivo", "파일 없음", "Arquivo ausente", "Fichier manquant", "Thiếu tệp", "文件缺失", "फ़ाइल उपलब्ध नहीं"),
    ('Delete folder "{name}"? {count} PDF file(s) will become unfiled.', 'Ordner „{name}“ löschen? {count} PDF-Datei(en) werden danach nicht zugeordnet.', '¿Eliminar la carpeta «{name}»? {count} archivo(s) PDF quedarán sin archivar.', '“{name}” 폴더를 삭제할까요? PDF 파일 {count}개가 미분류 상태가 됩니다.', 'Excluir a pasta “{name}”? {count} arquivo(s) PDF ficarão sem pasta.', 'Supprimer le dossier « {name} » ? {count} fichier(s) PDF ne seront plus classés.', 'Xóa thư mục “{name}”? {count} tệp PDF sẽ không còn được phân loại.', '删除文件夹“{name}”？{count} 个 PDF 文件将变为未归档。', 'फ़ोल्डर “{name}” हटाएँ? {count} PDF फ़ाइलें अवर्गीकृत हो जाएँगी।'),
    ("Loading…", "Wird geladen …", "Cargando…", "불러오는 중…", "Carregando…", "Chargement…", "Đang tải…", "正在加载…", "लोड हो रहा है…"),
    ("Page {page}: {error}", "Seite {page}: {error}", "Página {page}: {error}", "페이지 {page}: {error}", "Página {page}: {error}", "Page {page} : {error}", "Trang {page}: {error}", "第 {page} 页：{error}", "पृष्ठ {page}: {error}"),
    ("Could not copy text", "Text konnte nicht kopiert werden", "No se pudo copiar el texto", "텍스트를 복사하지 못했습니다", "Não foi possível copiar o texto", "Impossible de copier le texte", "Không thể sao chép văn bản", "无法复制文本", "पाठ कॉपी नहीं हो सका"),
    ("Cards created", "Karten erstellt", "Tarjetas creadas", "카드를 만들었습니다", "Cartões criados", "Cartes créées", "Đã tạo thẻ", "已创建卡片", "कार्ड बनाए गए"),
    ("Could not create cards", "Karten konnten nicht erstellt werden", "No se pudieron crear las tarjetas", "카드를 만들지 못했습니다", "Não foi possível criar os cartões", "Impossible de créer les cartes", "Không thể tạo thẻ", "无法创建卡片", "कार्ड नहीं बनाए जा सके"),
])


# Mind map: editor controls, dialogs, import/export and learning mode.
_add_rows([
    ("Edit Hints", "Hinweise bearbeiten", "Editar pistas", "힌트 편집", "Editar dicas", "Modifier les indices", "Sửa gợi ý", "编辑提示", "संकेत संपादित करें"),
    ("{count} selected", "{count} ausgewählt", "{count} seleccionados", "{count}개 선택됨", "{count} selecionados", "{count} sélectionnés", "Đã chọn {count}", "已选择 {count} 个", "{count} चुने गए"),
    ("Enter here...", "Hier eingeben …", "Escribe aquí...", "여기에 입력하세요...", "Digite aqui...", "Saisissez ici…", "Nhập tại đây...", "在此输入…", "यहाँ लिखें..."),
    ("Confirm", "Bestätigen", "Confirmar", "확인", "Confirmar", "Confirmer", "Xác nhận", "确认", "पुष्टि करें"),
    ("Undo (Ctrl+Z)", "Rückgängig (Strg+Z)", "Deshacer (Ctrl+Z)", "실행 취소(Ctrl+Z)", "Desfazer (Ctrl+Z)", "Annuler (Ctrl+Z)", "Hoàn tác (Ctrl+Z)", "撤销（Ctrl+Z）", "पूर्ववत करें (Ctrl+Z)"),
    ("Redo (Ctrl+Y)", "Wiederholen (Strg+Y)", "Rehacer (Ctrl+Y)", "다시 실행(Ctrl+Y)", "Refazer (Ctrl+Y)", "Rétablir (Ctrl+Y)", "Làm lại (Ctrl+Y)", "重做（Ctrl+Y）", "फिर करें (Ctrl+Y)"),
    ("Mind Map error", "Mindmap-Fehler", "Error del mapa mental", "마인드맵 오류", "Erro no mapa mental", "Erreur de carte mentale", "Lỗi sơ đồ tư duy", "思维导图错误", "माइंड मैप त्रुटि"),
    ("Basic Controls", "Grundbedienung", "Controles básicos", "기본 조작", "Controles básicos", "Commandes de base", "Điều khiển cơ bản", "基本操作", "मूल नियंत्रण"),
    ("Pan View: Click and drag on the empty background.", "Ansicht verschieben: Auf den leeren Hintergrund klicken und ziehen.", "Mover la vista: haz clic y arrastra el fondo vacío.", "화면 이동: 빈 배경을 클릭해 드래그하세요.", "Mover a visualização: clique e arraste o fundo vazio.", "Déplacer la vue : cliquez et faites glisser l’arrière-plan vide.", "Di chuyển khung nhìn: nhấp và kéo nền trống.", "平移视图：点击并拖动空白背景。", "दृश्य खिसकाएँ: खाली पृष्ठभूमि पर क्लिक करके खींचें।"),
    ("Zoom View: Use the mouse wheel or the +/- buttons.", "Ansicht zoomen: Mausrad oder Schaltflächen +/− verwenden.", "Zoom: usa la rueda del ratón o los botones +/−.", "확대/축소: 마우스 휠이나 +/− 버튼을 사용하세요.", "Zoom: use a roda do mouse ou os botões +/−.", "Zoomer : utilisez la molette ou les boutons +/−.", "Thu phóng: dùng con lăn chuột hoặc nút +/−.", "缩放视图：使用鼠标滚轮或 +/− 按钮。", "ज़ूम करें: माउस व्हील या +/− बटन उपयोग करें।"),
    ("Move Node: Click and drag any node.", "Knoten verschieben: Einen Knoten anklicken und ziehen.", "Mover nodo: haz clic y arrastra cualquier nodo.", "노드 이동: 노드를 클릭해 드래그하세요.", "Mover nó: clique e arraste qualquer nó.", "Déplacer un nœud : cliquez et faites glisser un nœud.", "Di chuyển nút: nhấp và kéo bất kỳ nút nào.", "移动节点：点击并拖动任意节点。", "नोड खिसकाएँ: किसी नोड पर क्लिक करके खींचें।"),
    ("Create Child Node: Click and drag the blue dot on a node.", "Unterknoten erstellen: Den blauen Punkt eines Knotens anklicken und ziehen.", "Crear nodo hijo: haz clic y arrastra el punto azul de un nodo.", "하위 노드 만들기: 노드의 파란 점을 클릭해 드래그하세요.", "Criar nó filho: clique e arraste o ponto azul de um nó.", "Créer un nœud enfant : cliquez et faites glisser le point bleu d’un nœud.", "Tạo nút con: nhấp và kéo chấm xanh trên một nút.", "创建子节点：点击并拖动节点上的蓝点。", "चाइल्ड नोड बनाएँ: नोड के नीले बिंदु को क्लिक करके खींचें।"),
    ("Undo/Redo: Use the arrows at the top right or Ctrl+Z / Ctrl+Y.", "Rückgängig/Wiederholen: Pfeile oben rechts oder Strg+Z / Strg+Y verwenden.", "Deshacer/rehacer: usa las flechas superiores o Ctrl+Z / Ctrl+Y.", "실행 취소/다시 실행: 오른쪽 위 화살표 또는 Ctrl+Z / Ctrl+Y를 사용하세요.", "Desfazer/refazer: use as setas no canto superior direito ou Ctrl+Z / Ctrl+Y.", "Annuler/rétablir : utilisez les flèches en haut à droite ou Ctrl+Z / Ctrl+Y.", "Hoàn tác/làm lại: dùng mũi tên góc trên bên phải hoặc Ctrl+Z / Ctrl+Y.", "撤销/重做：使用右上角箭头或 Ctrl+Z / Ctrl+Y。", "पूर्ववत/फिर करें: ऊपर दाएँ तीर या Ctrl+Z / Ctrl+Y उपयोग करें।"),
    ("Edit Text: Double-click the text inside a node.", "Text bearbeiten: Den Text im Knoten doppelklicken.", "Editar texto: haz doble clic en el texto del nodo.", "텍스트 편집: 노드 안의 텍스트를 두 번 클릭하세요.", "Editar texto: clique duas vezes no texto do nó.", "Modifier le texte : double-cliquez sur le texte d’un nœud.", "Sửa văn bản: nhấp đúp vào văn bản trong nút.", "编辑文本：双击节点内的文本。", "पाठ संपादित करें: नोड के भीतर पाठ पर डबल-क्लिक करें।"),
    ("Features", "Funktionen", "Funciones", "기능", "Recursos", "Fonctionnalités", "Tính năng", "功能", "सुविधाएँ"),
    ("New Map / Delete Map: Manage your mind maps.", "Neue Map / Map löschen: Mindmaps verwalten.", "Nuevo mapa / Eliminar mapa: gestiona tus mapas mentales.", "새 맵 / 맵 삭제: 마인드맵을 관리합니다.", "Novo mapa / Excluir mapa: gerencie seus mapas mentais.", "Nouvelle carte / Supprimer la carte : gérez vos cartes mentales.", "Sơ đồ mới / Xóa sơ đồ: quản lý sơ đồ tư duy.", "新建/删除导图：管理你的思维导图。", "नया मैप / मैप हटाएँ: अपने माइंड मैप प्रबंधित करें।"),
    ("Create with AI: Generate a mind map from a topic using AI.", "Mit KI erstellen: Aus einem Thema eine Mindmap erzeugen.", "Crear con IA: genera un mapa mental a partir de un tema.", "AI로 만들기: 주제로 마인드맵을 생성합니다.", "Criar com IA: gere um mapa mental a partir de um tema.", "Créer avec l’IA : générez une carte mentale à partir d’un sujet.", "Tạo bằng AI: tạo sơ đồ tư duy từ một chủ đề.", "使用 AI 创建：根据主题生成思维导图。", "AI से बनाएँ: किसी विषय से माइंड मैप बनाएँ।"),
    ("Start Learning: Review mode with active recall.", "Lernen starten: Wiederholungsmodus mit aktivem Abruf.", "Empezar a aprender: repaso mediante recuerdo activo.", "학습 시작: 능동 회상 복습 모드입니다.", "Iniciar estudo: modo de revisão com recordação ativa.", "Commencer l’apprentissage : révision par rappel actif.", "Bắt đầu học: chế độ ôn bằng gợi nhớ chủ động.", "开始学习：使用主动回忆进行复习。", "सीखना शुरू करें: सक्रिय स्मरण वाला समीक्षा मोड।"),
    ("Mind Map Information", "Mindmap-Informationen", "Información del mapa mental", "마인드맵 정보", "Informações do mapa mental", "Informations sur la carte mentale", "Thông tin sơ đồ tư duy", "思维导图信息", "माइंड मैप जानकारी"),
    ("Step 1: Customize and Copy the Prompt", "Schritt 1: Prompt anpassen und kopieren", "Paso 1: personaliza y copia el prompt", "1단계: 프롬프트 수정 및 복사", "Etapa 1: personalize e copie o prompt", "Étape 1 : personnalisez et copiez le prompt", "Bước 1: tùy chỉnh và sao chép lời nhắc", "第 1 步：自定义并复制提示词", "चरण 1: प्रॉम्प्ट बदलें और कॉपी करें"),
    ("Copy Prompt", "Prompt kopieren", "Copiar prompt", "프롬프트 복사", "Copiar prompt", "Copier le prompt", "Sao chép lời nhắc", "复制提示词", "प्रॉम्प्ट कॉपी करें"),
    ("Step 2: Paste the AI-Generated JSON", "Schritt 2: KI-erzeugtes JSON einfügen", "Paso 2: pega el JSON generado por la IA", "2단계: AI가 생성한 JSON 붙여넣기", "Etapa 2: cole o JSON gerado pela IA", "Étape 2 : collez le JSON généré par l’IA", "Bước 2: dán JSON do AI tạo", "第 2 步：粘贴 AI 生成的 JSON", "चरण 2: AI से बना JSON चिपकाएँ"),
    ("Paste JSON here...", "JSON hier einfügen …", "Pega el JSON aquí...", "여기에 JSON을 붙여넣으세요...", "Cole o JSON aqui...", "Collez le JSON ici…", "Dán JSON tại đây...", "在此粘贴 JSON…", "JSON यहाँ चिपकाएँ..."),
    ("Import Mind Map", "Mindmap importieren", "Importar mapa mental", "마인드맵 가져오기", "Importar mapa mental", "Importer la carte mentale", "Nhập sơ đồ tư duy", "导入思维导图", "माइंड मैप आयात करें"),
])

_add_rows([
    ("The current mind map could not be saved. Import was cancelled to protect your changes.", "Die aktuelle Mindmap konnte nicht gespeichert werden. Der Import wurde zum Schutz deiner Änderungen abgebrochen.", "No se pudo guardar el mapa actual. La importación se canceló para proteger tus cambios.", "현재 마인드맵을 저장하지 못했습니다. 변경 사항 보호를 위해 가져오기를 취소했습니다.", "Não foi possível salvar o mapa atual. A importação foi cancelada para proteger suas alterações.", "La carte mentale actuelle n’a pas pu être enregistrée. L’importation a été annulée pour protéger vos modifications.", "Không thể lưu sơ đồ hiện tại. Việc nhập đã bị hủy để bảo vệ thay đổi của bạn.", "无法保存当前思维导图。为保护你的更改，导入已取消。", "मौजूदा माइंड मैप सहेजा नहीं जा सका। आपके बदलाव बचाने के लिए आयात रद्द किया गया।"),
    ("Please paste your mind map JSON first.", "Füge zuerst das JSON deiner Mindmap ein.", "Pega primero el JSON de tu mapa mental.", "먼저 마인드맵 JSON을 붙여넣으세요.", "Cole primeiro o JSON do mapa mental.", "Collez d’abord le JSON de votre carte mentale.", "Hãy dán JSON của sơ đồ tư duy trước.", "请先粘贴思维导图 JSON。", "पहले अपने माइंड मैप का JSON चिपकाएँ।"),
    ("Invalid JSON: {error}. Make sure you copied the complete JSON object.", "Ungültiges JSON: {error}. Stelle sicher, dass du das vollständige JSON-Objekt kopiert hast.", "JSON no válido: {error}. Asegúrate de haber copiado el objeto JSON completo.", "잘못된 JSON: {error}. 전체 JSON 객체를 복사했는지 확인하세요.", "JSON inválido: {error}. Verifique se copiou o objeto JSON completo.", "JSON non valide : {error}. Vérifiez que vous avez copié l’objet JSON complet.", "JSON không hợp lệ: {error}. Hãy đảm bảo bạn đã sao chép toàn bộ đối tượng JSON.", "JSON 无效：{error}。请确认已复制完整的 JSON 对象。", "अमान्य JSON: {error}। सुनिश्चित करें कि पूरा JSON ऑब्जेक्ट कॉपी किया गया है।"),
    ("This JSON is not a valid mind map: {error}", "Dieses JSON ist keine gültige Mindmap: {error}", "Este JSON no es un mapa mental válido: {error}", "이 JSON은 유효한 마인드맵이 아닙니다: {error}", "Este JSON não é um mapa mental válido: {error}", "Ce JSON n’est pas une carte mentale valide : {error}", "JSON này không phải sơ đồ tư duy hợp lệ: {error}", "此 JSON 不是有效的思维导图：{error}", "यह JSON मान्य माइंड मैप नहीं है: {error}"),
    ("The mind map is valid but could not be saved (storage full?).", "Die Mindmap ist gültig, konnte aber nicht gespeichert werden (Speicher voll?).", "El mapa es válido, pero no se pudo guardar (¿almacenamiento lleno?).", "마인드맵은 유효하지만 저장하지 못했습니다(저장 공간이 가득 찼나요?).", "O mapa é válido, mas não pôde ser salvo (armazenamento cheio?).", "La carte est valide, mais n’a pas pu être enregistrée (stockage plein ?).", "Sơ đồ hợp lệ nhưng không thể lưu (bộ nhớ đầy?).", "思维导图有效，但无法保存（存储空间已满？）。", "माइंड मैप मान्य है लेकिन सहेजा नहीं जा सका (स्टोरेज भरा है?)।"),
    ("Import failed while loading the map: {error}", "Der Import ist beim Laden der Mindmap fehlgeschlagen: {error}", "La importación falló al cargar el mapa: {error}", "맵을 불러오는 중 가져오기에 실패했습니다: {error}", "A importação falhou ao carregar o mapa: {error}", "L’importation a échoué lors du chargement de la carte : {error}", "Nhập thất bại khi tải sơ đồ: {error}", "加载导图时导入失败：{error}", "मैप लोड करते समय आयात विफल हुआ: {error}"),
    ("Mind map imported. Some data was repaired automatically: {details}", "Mindmap importiert. Einige Daten wurden automatisch repariert: {details}", "Mapa importado. Algunos datos se repararon automáticamente: {details}", "마인드맵을 가져왔습니다. 일부 데이터를 자동으로 복구했습니다: {details}", "Mapa importado. Alguns dados foram reparados automaticamente: {details}", "Carte mentale importée. Certaines données ont été réparées automatiquement : {details}", "Đã nhập sơ đồ. Một số dữ liệu được tự động sửa: {details}", "思维导图已导入。部分数据已自动修复：{details}", "माइंड मैप आयात हुआ। कुछ डेटा अपने आप ठीक किया गया: {details}"),
    ("Unnamed Map", "Unbenannte Mindmap", "Mapa sin nombre", "이름 없는 맵", "Mapa sem nome", "Carte sans nom", "Sơ đồ chưa đặt tên", "未命名导图", "बेनाम मैप"),
    ("Create New Mind Map", "Neue Mindmap erstellen", "Crear un mapa mental", "새 마인드맵 만들기", "Criar novo mapa mental", "Créer une carte mentale", "Tạo sơ đồ tư duy mới", "新建思维导图", "नया माइंड मैप बनाएँ"),
    ("Please enter a name.", "Gib bitte einen Namen ein.", "Introduce un nombre.", "이름을 입력하세요.", "Digite um nome.", "Saisissez un nom.", "Hãy nhập tên.", "请输入名称。", "कृपया नाम दर्ज करें।"),
    ("Create", "Erstellen", "Crear", "만들기", "Criar", "Créer", "Tạo", "创建", "बनाएँ"),
    ("Central Topic", "Zentrales Thema", "Tema central", "중심 주제", "Tema central", "Sujet central", "Chủ đề trung tâm", "中心主题", "मुख्य विषय"),
    ("Import from JSON", "Aus JSON importieren", "Importar desde JSON", "JSON에서 가져오기", "Importar de JSON", "Importer depuis JSON", "Nhập từ JSON", "从 JSON 导入", "JSON से आयात करें"),
    ("Paste your mind map JSON data below.", "Füge unten die JSON-Daten deiner Mindmap ein.", "Pega debajo los datos JSON de tu mapa mental.", "아래에 마인드맵 JSON 데이터를 붙여넣으세요.", "Cole abaixo os dados JSON do mapa mental.", "Collez ci-dessous les données JSON de votre carte mentale.", "Dán dữ liệu JSON của sơ đồ tư duy bên dưới.", "在下方粘贴思维导图 JSON 数据。", "अपने माइंड मैप का JSON डेटा नीचे चिपकाएँ।"),
    ("Export to JSON", "Als JSON exportieren", "Exportar a JSON", "JSON으로 내보내기", "Exportar para JSON", "Exporter en JSON", "Xuất sang JSON", "导出为 JSON", "JSON में निर्यात करें"),
    ("Copy the JSON data below.", "Kopiere die unten stehenden JSON-Daten.", "Copia los datos JSON de abajo.", "아래 JSON 데이터를 복사하세요.", "Copie os dados JSON abaixo.", "Copiez les données JSON ci-dessous.", "Sao chép dữ liệu JSON bên dưới.", "复制下方 JSON 数据。", "नीचे का JSON डेटा कॉपी करें।"),
    ("Copy to Clipboard", "In Zwischenablage kopieren", "Copiar al portapapeles", "클립보드에 복사", "Copiar para a área de transferência", "Copier dans le presse-papiers", "Sao chép vào bộ nhớ tạm", "复制到剪贴板", "क्लिपबोर्ड पर कॉपी करें"),
    ("Nothing to export: the current mind map was not found in storage.", "Nichts zu exportieren: Die aktuelle Mindmap wurde nicht im Speicher gefunden.", "No hay nada que exportar: el mapa actual no está en el almacenamiento.", "내보낼 내용이 없습니다. 저장소에서 현재 마인드맵을 찾지 못했습니다.", "Nada para exportar: o mapa atual não foi encontrado no armazenamento.", "Rien à exporter : la carte actuelle est introuvable dans le stockage.", "Không có gì để xuất: không tìm thấy sơ đồ hiện tại trong bộ nhớ.", "没有可导出的内容：存储中找不到当前思维导图。", "निर्यात के लिए कुछ नहीं: मौजूदा माइंड मैप स्टोरेज में नहीं मिला।"),
    ("Color", "Farbe", "Color", "색상", "Cor", "Couleur", "Màu", "颜色", "रंग"),
    ("Size", "Größe", "Tamaño", "크기", "Tamanho", "Taille", "Kích thước", "大小", "आकार"),
    ("Small", "Klein", "Pequeño", "작게", "Pequeno", "Petit", "Nhỏ", "小", "छोटा"),
    ("Medium", "Mittel", "Mediano", "보통", "Médio", "Moyen", "Vừa", "中", "मध्यम"),
    ("Large", "Groß", "Grande", "크게", "Grande", "Grand", "Lớn", "大", "बड़ा"),
])

_add_rows([
    ("Delete this map?", "Diese Mindmap löschen?", "¿Eliminar este mapa?", "이 맵을 삭제할까요?", "Excluir este mapa?", "Supprimer cette carte ?", "Xóa sơ đồ này?", "删除此导图？", "यह मैप हटाएँ?"),
    ("Resize", "Größe ändern", "Cambiar tamaño", "크기 조절", "Redimensionar", "Redimensionner", "Đổi kích thước", "调整大小", "आकार बदलें"),
    ("Hint…", "Hinweis …", "Pista…", "힌트…", "Dica…", "Indice…", "Gợi ý…", "提示…", "संकेत…"),
    ("New Node", "Neuer Knoten", "Nuevo nodo", "새 노드", "Novo nó", "Nouveau nœud", "Nút mới", "新节点", "नया नोड"),
    ("Delete node?", "Knoten löschen?", "¿Eliminar nodo?", "노드를 삭제할까요?", "Excluir nó?", "Supprimer le nœud ?", "Xóa nút?", "删除节点？", "नोड हटाएँ?"),
    ("Reviewing missed cards…", "Nicht gewusste Karten werden wiederholt …", "Repasando las tarjetas falladas…", "틀린 카드를 복습하는 중…", "Revisando cartões errados…", "Révision des cartes manquées…", "Đang ôn các thẻ chưa nhớ…", "正在复习未答对的卡片…", "छूटे कार्ड दोहराए जा रहे हैं…"),
    ("Done! Great work!", "Fertig! Gute Arbeit!", "¡Terminado! ¡Buen trabajo!", "완료! 잘했어요!", "Concluído! Muito bem!", "Terminé ! Bravo !", "Xong! Làm tốt lắm!", "完成！做得很好！", "पूरा हुआ! बहुत बढ़िया!"),
    ("Recall the highlighted node · {remaining} remaining", "Erinnere dich an den markierten Knoten · noch {remaining}", "Recuerda el nodo resaltado · quedan {remaining}", "강조된 노드를 떠올려 보세요 · {remaining}개 남음", "Lembre-se do nó destacado · faltam {remaining}", "Rappelez-vous le nœud surligné · {remaining} restant(s)", "Hãy nhớ nút được tô sáng · còn {remaining}", "回忆高亮节点 · 剩余 {remaining}", "हाइलाइट किया नोड याद करें · {remaining} बाकी"),
    ("Did you recall it correctly?", "Hast du dich richtig erinnert?", "¿Lo recordaste correctamente?", "정확히 기억했나요?", "Você se lembrou corretamente?", "Vous en êtes-vous souvenu correctement ?", "Bạn đã nhớ đúng chưa?", "你回忆正确了吗？", "क्या आपने इसे सही याद किया?"),
])

_add_rows([
    ("Storage read failed", "Lesen des Speichers fehlgeschlagen", "Error al leer el almacenamiento", "저장소 읽기 실패", "Falha ao ler o armazenamento", "Échec de lecture du stockage", "Không thể đọc bộ nhớ", "读取存储失败", "स्टोरेज पढ़ना विफल"),
    ("Stored mind map data was corrupted and has been backed up. Starting fresh.", "Gespeicherte Mindmap-Daten waren beschädigt und wurden gesichert. Es wird neu begonnen.", "Los datos guardados estaban dañados y se han respaldado. Se empezará de nuevo.", "저장된 마인드맵 데이터가 손상되어 백업했습니다. 새로 시작합니다.", "Os dados salvos estavam corrompidos e foram copiados. Um novo conjunto será iniciado.", "Les données enregistrées étaient endommagées et ont été sauvegardées. Un nouvel ensemble va être créé.", "Dữ liệu sơ đồ đã lưu bị hỏng và đã được sao lưu. Sẽ bắt đầu lại.", "已保存的思维导图数据损坏，现已备份。将重新开始。", "सहेजा माइंड मैप डेटा खराब था और उसका बैकअप बना दिया गया। नए सिरे से शुरू किया जा रहा है।"),
    ("Could not save: browser storage is full. Export your maps as backup and delete unused maps.", "Speichern nicht möglich: Der Browserspeicher ist voll. Exportiere deine Mindmaps als Sicherung und lösche ungenutzte Maps.", "No se pudo guardar: el almacenamiento está lleno. Exporta los mapas como copia y elimina los que no uses.", "저장소가 가득 차 저장할 수 없습니다. 맵을 백업으로 내보내고 사용하지 않는 맵을 삭제하세요.", "Não foi possível salvar: o armazenamento está cheio. Exporte os mapas como backup e exclua os que não usa.", "Enregistrement impossible : le stockage est plein. Exportez vos cartes puis supprimez celles qui sont inutilisées.", "Không thể lưu: bộ nhớ trình duyệt đã đầy. Hãy xuất sơ đồ để sao lưu và xóa sơ đồ không dùng.", "无法保存：浏览器存储空间已满。请导出导图作为备份并删除不用的导图。", "सहेजा नहीं जा सका: ब्राउज़र स्टोरेज भरा है। मैप निर्यात करके बैकअप लें और अनुपयोगी मैप हटाएँ।"),
    ("Could not save mind maps: {error}", "Mindmaps konnten nicht gespeichert werden: {error}", "No se pudieron guardar los mapas: {error}", "마인드맵을 저장하지 못했습니다: {error}", "Não foi possível salvar os mapas: {error}", "Impossible d’enregistrer les cartes mentales : {error}", "Không thể lưu sơ đồ tư duy: {error}", "无法保存思维导图：{error}", "माइंड मैप सहेजे नहीं जा सके: {error}"),
    ("Recovery data is invalid", "Wiederherstellungsdaten sind ungültig", "Los datos de recuperación no son válidos", "복구 데이터가 유효하지 않음", "Os dados de recuperação são inválidos", "Les données de récupération ne sont pas valides", "Dữ liệu khôi phục không hợp lệ", "恢复数据无效", "रिकवरी डेटा अमान्य है"),
    ("A newer mind map recovery copy was restored.", "Eine neuere Sicherungskopie der Mindmap wurde wiederhergestellt.", "Se restauró una copia de recuperación más reciente.", "더 최신의 마인드맵 복구 사본을 복원했습니다.", "Uma cópia de recuperação mais recente foi restaurada.", "Une copie de récupération plus récente a été restaurée.", "Đã khôi phục bản sao sơ đồ mới hơn.", "已恢复较新的思维导图备份。", "माइंड मैप की नई रिकवरी कॉपी बहाल की गई।"),
    ("Your recovery copy is open in memory. Free browser storage or export it before closing.", "Die Sicherungskopie ist im Arbeitsspeicher geöffnet. Gib Browserspeicher frei oder exportiere sie vor dem Schließen.", "La copia de recuperación está abierta en memoria. Libera espacio o expórtala antes de cerrar.", "복구 사본이 메모리에 열려 있습니다. 닫기 전에 저장 공간을 확보하거나 내보내세요.", "A cópia de recuperação está aberta na memória. Libere espaço ou exporte-a antes de fechar.", "La copie de récupération est ouverte en mémoire. Libérez de l’espace ou exportez-la avant de fermer.", "Bản khôi phục đang mở trong bộ nhớ. Hãy giải phóng dung lượng hoặc xuất trước khi đóng.", "恢复副本已在内存中打开。关闭前请释放存储空间或将其导出。", "रिकवरी कॉपी मेमोरी में खुली है। बंद करने से पहले स्टोरेज खाली करें या निर्यात करें।"),
    ("{count} corrupted mind map(s) were removed so the tool works again. A backup was kept in storage.", "{count} beschädigte Mindmap(s) wurden entfernt, damit das Werkzeug wieder funktioniert. Eine Sicherung blieb gespeichert.", "Se eliminaron {count} mapa(s) dañados para que la herramienta vuelva a funcionar. Se conservó una copia.", "도구가 다시 작동하도록 손상된 마인드맵 {count}개를 제거했습니다. 백업은 저장소에 보관했습니다.", "Foram removidos {count} mapa(s) corrompidos para a ferramenta voltar a funcionar. Um backup foi mantido.", "{count} carte(s) endommagée(s) ont été supprimées afin de rétablir l’outil. Une sauvegarde a été conservée.", "Đã xóa {count} sơ đồ bị hỏng để công cụ hoạt động lại. Bản sao lưu vẫn được giữ.", "已移除 {count} 个损坏的思维导图，使工具恢复工作；备份仍保留在存储中。", "टूल चलाने के लिए {count} खराब माइंड मैप हटाए गए। बैकअप स्टोरेज में रखा गया।"),
    ("{count} mind map(s) had invalid data and were repaired automatically.", "{count} Mindmap(s) enthielten ungültige Daten und wurden automatisch repariert.", "{count} mapa(s) contenían datos no válidos y se repararon automáticamente.", "마인드맵 {count}개에 잘못된 데이터가 있어 자동으로 복구했습니다.", "{count} mapa(s) tinham dados inválidos e foram reparados automaticamente.", "{count} carte(s) contenaient des données non valides et ont été réparées automatiquement.", "{count} sơ đồ có dữ liệu không hợp lệ và đã được tự động sửa.", "{count} 个思维导图包含无效数据，现已自动修复。", "{count} माइंड मैप में अमान्य डेटा था और उन्हें अपने आप ठीक किया गया।"),
    ("Startup check", "Startprüfung", "Comprobación inicial", "시작 검사", "Verificação inicial", "Vérification au démarrage", "Kiểm tra khi khởi động", "启动检查", "स्टार्टअप जाँच"),
    ("Loading mind map", "Mindmap wird geladen", "Cargando mapa mental", "마인드맵 불러오는 중", "Carregando mapa mental", "Chargement de la carte mentale", "Đang tải sơ đồ tư duy", "正在加载思维导图", "माइंड मैप लोड हो रहा है"),
    ("This mind map was corrupted and has been removed. A backup was kept in storage.", "Diese Mindmap war beschädigt und wurde entfernt. Eine Sicherung blieb gespeichert.", "Este mapa estaba dañado y se eliminó. Se conservó una copia de seguridad.", "이 마인드맵은 손상되어 제거했습니다. 백업은 저장소에 보관했습니다.", "Este mapa estava corrompido e foi removido. Um backup foi mantido.", "Cette carte était endommagée et a été supprimée. Une sauvegarde a été conservée.", "Sơ đồ này bị hỏng và đã bị xóa. Bản sao lưu vẫn được giữ.", "此思维导图已损坏并被移除；备份仍保留在存储中。", "यह माइंड मैप खराब था और हटा दिया गया। बैकअप स्टोरेज में रखा गया।"),
    ("Initialization", "Initialisierung", "Inicialización", "초기화", "Inicialização", "Initialisation", "Khởi tạo", "初始化", "आरंभीकरण"),
])

_add_rows([
    ("You are an expert assistant that creates mind maps in a specific JSON format.", "Du bist ein fachkundiger Assistent, der Mindmaps in einem bestimmten JSON-Format erstellt.", "Eres un asistente experto que crea mapas mentales en un formato JSON específico.", "당신은 특정 JSON 형식으로 마인드맵을 만드는 전문 도우미입니다.", "Você é um assistente especialista que cria mapas mentais em um formato JSON específico.", "Vous êtes un assistant expert qui crée des cartes mentales dans un format JSON précis.", "Bạn là trợ lý chuyên tạo sơ đồ tư duy theo một định dạng JSON cụ thể.", "你是一名专业助手，负责按指定 JSON 格式创建思维导图。", "आप एक विशेषज्ञ सहायक हैं जो विशेष JSON प्रारूप में माइंड मैप बनाते हैं।"),
    ("The output must be one valid JSON object and nothing else. Do not add explanations.", "Die Ausgabe muss genau ein gültiges JSON-Objekt enthalten. Füge keine Erklärungen hinzu.", "La salida debe ser un único objeto JSON válido. No añadas explicaciones.", "출력은 유효한 JSON 객체 하나여야 하며 설명을 추가하지 마세요.", "A saída deve conter apenas um objeto JSON válido. Não adicione explicações.", "La sortie doit contenir un seul objet JSON valide, sans aucune explication.", "Đầu ra phải chỉ là một đối tượng JSON hợp lệ. Không thêm lời giải thích.", "输出必须仅包含一个有效的 JSON 对象，不要添加说明。", "आउटपुट केवल एक मान्य JSON ऑब्जेक्ट होना चाहिए। कोई व्याख्या न जोड़ें।"),
    ("Use this JSON structure:", "Verwende diese JSON-Struktur:", "Usa esta estructura JSON:", "다음 JSON 구조를 사용하세요:", "Use esta estrutura JSON:", "Utilisez cette structure JSON :", "Dùng cấu trúc JSON sau:", "使用以下 JSON 结构：", "यह JSON संरचना उपयोग करें:"),
    ("Name of the Mind Map", "Name der Mindmap", "Nombre del mapa mental", "마인드맵 이름", "Nome do mapa mental", "Nom de la carte mentale", "Tên sơ đồ tư duy", "思维导图名称", "माइंड मैप का नाम"),
    ("Main Branch", "Hauptzweig", "Rama principal", "주요 가지", "Ramo principal", "Branche principale", "Nhánh chính", "主要分支", "मुख्य शाखा"),
    ("Sub-point", "Unterpunkt", "Subpunto", "하위 항목", "Subponto", "Sous-point", "Ý phụ", "子要点", "उप-बिंदु"),
    ("Generate the mind map JSON now.", "Erstelle jetzt das JSON der Mindmap.", "Genera ahora el JSON del mapa mental.", "이제 마인드맵 JSON을 생성하세요.", "Gere agora o JSON do mapa mental.", "Générez maintenant le JSON de la carte mentale.", "Hãy tạo JSON cho sơ đồ tư duy ngay bây giờ.", "现在生成思维导图 JSON。", "अब माइंड मैप JSON बनाएँ।"),
])

# Localized content of the default mind-map tutorial.
_add_rows([
    ("Mind Map Tutorial", "Mindmap-Tutorial", "Tutorial de mapas mentales", "마인드맵 튜토리얼", "Tutorial de mapa mental", "Tutoriel de carte mentale", "Hướng dẫn sơ đồ tư duy", "思维导图教程", "माइंड मैप ट्यूटोरियल"),
    ("Welcome to the Mind Map Tool!", "Willkommen beim Mindmap-Werkzeug!", "¡Te damos la bienvenida a la herramienta de mapas mentales!", "마인드맵 도구에 오신 것을 환영합니다!", "Boas-vindas à ferramenta de mapa mental!", "Bienvenue dans l’outil de carte mentale !", "Chào mừng đến với công cụ sơ đồ tư duy!", "欢迎使用思维导图工具！", "माइंड मैप टूल में स्वागत है!"),
    ("Center View: Use the Center View button to focus on the root node.", "Ansicht zentrieren: Mit der Schaltfläche „Ansicht zentrieren“ den Wurzelknoten fokussieren.", "Centrar vista: usa el botón Centrar vista para enfocar el nodo raíz.", "화면 중앙 맞춤: 중앙 맞춤 버튼으로 루트 노드에 초점을 맞추세요.", "Centralizar visualização: use o botão para focar o nó raiz.", "Centrer la vue : utilisez le bouton correspondant pour afficher le nœud racine.", "Căn giữa khung nhìn: dùng nút Căn giữa để tập trung vào nút gốc.", "居中视图：使用“居中视图”按钮聚焦根节点。", "दृश्य केंद्रित करें: रूट नोड पर जाने के लिए केंद्र बटन उपयोग करें।"),
    ("Managing Nodes", "Knoten verwalten", "Gestión de nodos", "노드 관리", "Gerenciamento de nós", "Gestion des nœuds", "Quản lý nút", "管理节点", "नोड प्रबंधन"),
    ("Delete Node: Hover over a node and use the minus button.", "Knoten löschen: Mit der Maus über einen Knoten fahren und die Minus-Schaltfläche verwenden.", "Eliminar nodo: pasa el cursor por un nodo y usa el botón menos.", "노드 삭제: 노드 위에 마우스를 올리고 빼기 버튼을 누르세요.", "Excluir nó: passe o cursor sobre o nó e use o botão de menos.", "Supprimer un nœud : survolez-le puis utilisez le bouton moins.", "Xóa nút: di chuột lên nút và dùng nút dấu trừ.", "删除节点：将鼠标悬停在节点上，然后使用减号按钮。", "नोड हटाएँ: नोड पर होवर करके माइनस बटन उपयोग करें।"),
    ("Customize Nodes (right-click)", "Knoten anpassen (Rechtsklick)", "Personalizar nodos (clic derecho)", "노드 꾸미기(오른쪽 클릭)", "Personalizar nós (clique com o botão direito)", "Personnaliser les nœuds (clic droit)", "Tùy chỉnh nút (nhấp chuột phải)", "自定义节点（右键单击）", "नोड अनुकूलित करें (राइट-क्लिक)"),
    ("Change Color: Right-click a node and choose a color.", "Farbe ändern: Einen Knoten rechtsklicken und eine Farbe auswählen.", "Cambiar color: haz clic derecho en un nodo y elige un color.", "색상 변경: 노드를 오른쪽 클릭하고 색상을 고르세요.", "Alterar cor: clique com o botão direito no nó e escolha uma cor.", "Changer la couleur : faites un clic droit sur un nœud et choisissez une couleur.", "Đổi màu: nhấp chuột phải vào nút và chọn màu.", "更改颜色：右键单击节点并选择颜色。", "रंग बदलें: नोड पर राइट-क्लिक करके रंग चुनें।"),
    ("Change Size: Right-click and choose Small, Medium, or Large.", "Größe ändern: Rechtsklicken und Klein, Mittel oder Groß auswählen.", "Cambiar tamaño: haz clic derecho y elige Pequeño, Mediano o Grande.", "크기 변경: 오른쪽 클릭 후 작게, 보통 또는 크게를 선택하세요.", "Alterar tamanho: clique com o botão direito e escolha Pequeno, Médio ou Grande.", "Changer la taille : faites un clic droit puis choisissez Petit, Moyen ou Grand.", "Đổi kích thước: nhấp chuột phải và chọn Nhỏ, Vừa hoặc Lớn.", "更改大小：右键单击并选择小、中或大。", "आकार बदलें: राइट-क्लिक करके छोटा, मध्यम या बड़ा चुनें।"),
    ("Special Features", "Besondere Funktionen", "Funciones especiales", "특별 기능", "Recursos especiais", "Fonctionnalités spéciales", "Tính năng đặc biệt", "特殊功能", "विशेष सुविधाएँ"),
    ("1. Select Create with AI in the menu.", "1. Wähle im Menü „Mit KI erstellen“.", "1. Selecciona Crear con IA en el menú.", "1. 메뉴에서 AI로 만들기를 선택하세요.", "1. Selecione Criar com IA no menu.", "1. Sélectionnez Créer avec l’IA dans le menu.", "1. Chọn Tạo bằng AI trong menu.", "1. 在菜单中选择“使用 AI 创建”。", "1. मेनू में AI से बनाएँ चुनें।"),
    ("2. Copy the prompt and paste it into an AI service.", "2. Kopiere den Prompt und füge ihn in einen KI-Dienst ein.", "2. Copia el prompt y pégalo en un servicio de IA.", "2. 프롬프트를 복사해 AI 서비스에 붙여넣으세요.", "2. Copie o prompt e cole-o em um serviço de IA.", "2. Copiez le prompt et collez-le dans un service d’IA.", "2. Sao chép lời nhắc và dán vào dịch vụ AI.", "2. 复制提示词并粘贴到 AI 服务中。", "2. प्रॉम्प्ट कॉपी करके AI सेवा में चिपकाएँ।"),
    ("3. Copy the AI's JSON response and paste it back into the tool.", "3. Kopiere die JSON-Antwort der KI und füge sie wieder in das Werkzeug ein.", "3. Copia la respuesta JSON de la IA y pégala en la herramienta.", "3. AI의 JSON 응답을 복사해 도구에 다시 붙여넣으세요.", "3. Copie a resposta JSON da IA e cole-a novamente na ferramenta.", "3. Copiez la réponse JSON de l’IA et collez-la dans l’outil.", "3. Sao chép phản hồi JSON của AI và dán lại vào công cụ.", "3. 复制 AI 的 JSON 回复并粘贴回工具。", "3. AI का JSON उत्तर कॉपी करके टूल में वापस चिपकाएँ।"),
    ("Turns your map into an active-recall session.", "Verwandelt deine Mindmap in eine Sitzung mit aktivem Abruf.", "Convierte tu mapa en una sesión de recuerdo activo.", "맵을 능동 회상 학습 세션으로 바꿉니다.", "Transforma seu mapa em uma sessão de recordação ativa.", "Transforme votre carte en séance de rappel actif.", "Biến sơ đồ thành phiên gợi nhớ chủ động.", "将导图转换为主动回忆练习。", "मैप को सक्रिय-स्मरण सत्र में बदलता है।"),
    ("Child nodes are hidden so you can recall them.", "Unterknoten werden verborgen, damit du dich an sie erinnern kannst.", "Los nodos hijos se ocultan para que puedas recordarlos.", "하위 노드를 숨겨 직접 떠올릴 수 있게 합니다.", "Os nós filhos ficam ocultos para você se lembrar deles.", "Les nœuds enfants sont masqués afin que vous puissiez vous en souvenir.", "Các nút con được ẩn để bạn tự nhớ lại.", "隐藏子节点，以便你进行回忆。", "चाइल्ड नोड छिपते हैं ताकि आप उन्हें याद कर सकें।"),
    ("Rate your answer to reinforce your memory.", "Bewerte deine Antwort, um dein Gedächtnis zu festigen.", "Evalúa tu respuesta para reforzar la memoria.", "답을 평가해 기억을 강화하세요.", "Avalie sua resposta para reforçar a memória.", "Évaluez votre réponse pour renforcer votre mémoire.", "Đánh giá câu trả lời để củng cố trí nhớ.", "评价你的回答以强化记忆。", "याददाश्त मजबूत करने के लिए अपने उत्तर का मूल्यांकन करें।"),
    ("Data & Maps", "Daten & Mindmaps", "Datos y mapas", "데이터 및 맵", "Dados e mapas", "Données et cartes", "Dữ liệu & sơ đồ", "数据与导图", "डेटा और मैप"),
    ("Use the list at the top left to switch between maps.", "Wechsle über die Liste oben links zwischen Mindmaps.", "Usa la lista superior izquierda para cambiar de mapa.", "왼쪽 위 목록에서 맵을 전환하세요.", "Use a lista no canto superior esquerdo para trocar de mapa.", "Utilisez la liste en haut à gauche pour changer de carte.", "Dùng danh sách góc trên bên trái để chuyển sơ đồ.", "使用左上角列表切换导图。", "मैप बदलने के लिए ऊपर बाईं सूची उपयोग करें।"),
    ("New Map and Delete Map manage your collection.", "Mit „Neue Map“ und „Map löschen“ verwaltest du deine Sammlung.", "Nuevo mapa y Eliminar mapa gestionan tu colección.", "새 맵과 맵 삭제로 컬렉션을 관리합니다.", "Novo mapa e Excluir mapa gerenciam sua coleção.", "Nouvelle carte et Supprimer la carte gèrent votre collection.", "Sơ đồ mới và Xóa sơ đồ dùng để quản lý bộ sưu tập.", "使用“新建导图”和“删除导图”管理集合。", "नया मैप और मैप हटाएँ से अपना संग्रह प्रबंधित करें।"),
    ("Import / Export (backup)", "Import / Export (Sicherung)", "Importar / Exportar (copia)", "가져오기 / 내보내기(백업)", "Importar / Exportar (backup)", "Importer / Exporter (sauvegarde)", "Nhập / Xuất (sao lưu)", "导入/导出（备份）", "आयात / निर्यात (बैकअप)"),
    ("Export saves your map as JSON for backup.", "Der Export speichert deine Mindmap als JSON-Sicherung.", "Exportar guarda el mapa como JSON para crear una copia.", "내보내기는 맵을 백업용 JSON으로 저장합니다.", "Exportar salva seu mapa como JSON para backup.", "L’exportation enregistre votre carte au format JSON pour la sauvegarder.", "Xuất sẽ lưu sơ đồ dưới dạng JSON để sao lưu.", "导出会将导图保存为 JSON 备份。", "निर्यात आपके मैप को बैकअप के लिए JSON में सहेजता है।"),
    ("Import loads a map from a JSON file.", "Der Import lädt eine Mindmap aus einer JSON-Datei.", "Importar carga un mapa desde un archivo JSON.", "가져오기는 JSON 파일에서 맵을 불러옵니다.", "Importar carrega um mapa de um arquivo JSON.", "L’importation charge une carte depuis un fichier JSON.", "Nhập sẽ tải sơ đồ từ tệp JSON.", "导入会从 JSON 文件加载导图。", "आयात JSON फ़ाइल से मैप लोड करता है।"),
])

_add_rows([
    ("Could not load the SoundCloud player.", "Der SoundCloud-Player konnte nicht geladen werden.", "No se pudo cargar el reproductor de SoundCloud.", "SoundCloud 플레이어를 불러오지 못했습니다.", "Não foi possível carregar o player do SoundCloud.", "Impossible de charger le lecteur SoundCloud.", "Không thể tải trình phát SoundCloud.", "无法加载 SoundCloud 播放器。", "SoundCloud प्लेयर लोड नहीं हो सका।"),
    ("Check your internet connection.", "Prüfe deine Internetverbindung.", "Comprueba tu conexión a internet.", "인터넷 연결을 확인하세요.", "Verifique sua conexão com a internet.", "Vérifiez votre connexion Internet.", "Hãy kiểm tra kết nối Internet.", "请检查网络连接。", "अपना इंटरनेट कनेक्शन जाँचें।"),
    ("SoundCloud could not load this URL", "SoundCloud konnte diese URL nicht laden", "SoundCloud no pudo cargar esta URL", "SoundCloud가 이 URL을 불러오지 못했습니다", "O SoundCloud não pôde carregar esta URL", "SoundCloud n’a pas pu charger cette URL", "SoundCloud không thể tải URL này", "SoundCloud 无法加载此 URL", "SoundCloud यह URL लोड नहीं कर सका"),
    ("Widget API failed to load", "Die Widget-API konnte nicht geladen werden", "No se pudo cargar la API del widget", "위젯 API를 불러오지 못했습니다", "Falha ao carregar a API do widget", "Échec du chargement de l’API du widget", "Không thể tải API tiện ích", "Widget API 加载失败", "विजेट API लोड नहीं हुई"),
    ("Lo-Fi Focus", "Lo-Fi-Fokus", "Concentración lo-fi", "Lo-Fi 집중", "Foco lo-fi", "Concentration lo-fi", "Tập trung Lo-Fi", "Lo-Fi 专注", "लो-फाई फोकस"),
    ("Zoom out", "Verkleinern", "Alejar", "축소", "Reduzir zoom", "Dézoomer", "Thu nhỏ", "缩小", "ज़ूम आउट"),
    ("Zoom in", "Vergrößern", "Acercar", "확대", "Ampliar zoom", "Zoomer", "Phóng to", "放大", "ज़ूम इन"),
    ("Smart Study Gamification", "Smart Study-Gamifizierung", "Gamificación de Smart Study", "Smart Study 게임화", "Gamificação do Smart Study", "Gamification Smart Study", "Trò chơi hóa Smart Study", "Smart Study 游戏化", "Smart Study गेमिफिकेशन"),
])

_add_rows([
    ("Selected pages", "Ausgewählte Seiten", "Páginas seleccionadas", "선택한 페이지", "Páginas selecionadas", "Pages sélectionnées", "Các trang đã chọn", "已选页面", "चुने गए पृष्ठ"),
    ("Click PDF pages to select them.", "Klicke PDF-Seiten an, um sie auszuwählen.", "Haz clic en las páginas del PDF para seleccionarlas.", "PDF 페이지를 클릭해 선택하세요.", "Clique nas páginas do PDF para selecioná-las.", "Cliquez sur les pages du PDF pour les sélectionner.", "Nhấp vào các trang PDF để chọn.", "点击 PDF 页面进行选择。", "PDF पृष्ठ चुनने के लिए उन पर क्लिक करें।"),
    ("Current deck", "Aktueller Stapel", "Mazo actual", "현재 덱", "Baralho atual", "Paquet actuel", "Bộ thẻ hiện tại", "当前牌组", "वर्तमान डेक"),
    ("Recent decks", "Zuletzt verwendete Stapel", "Mazos recientes", "최근 덱", "Baralhos recentes", "Paquets récents", "Bộ thẻ gần đây", "最近使用的牌组", "हाल के डेक"),
    ("Decks", "Stapel", "Mazos", "덱", "Baralhos", "Paquets", "Bộ thẻ", "牌组", "डेक"),
    ("No matching decks. Enter a name to create one.", "Keine passenden Stapel. Gib einen Namen ein, um einen zu erstellen.", "No hay mazos coincidentes. Escribe un nombre para crear uno.", "일치하는 덱이 없습니다. 새 덱을 만들려면 이름을 입력하세요.", "Nenhum baralho correspondente. Digite um nome para criar um.", "Aucun paquet correspondant. Saisissez un nom pour en créer un.", "Không có bộ thẻ phù hợp. Nhập tên để tạo bộ thẻ mới.", "没有匹配的牌组。输入名称即可新建。", "कोई मिलता-जुलता डेक नहीं मिला। नया बनाने के लिए नाम दर्ज करें।"),
    ("Open PDF", "PDF öffnen", "Abrir PDF", "PDF 열기", "Abrir PDF", "Ouvrir le PDF", "Mở PDF", "打开 PDF", "PDF खोलें"),
    ("This linked PDF is not available on this device. Open the PDF library to relink it.", "Diese verknüpfte PDF ist auf diesem Gerät nicht verfügbar. Öffne die PDF-Bibliothek, um sie neu zu verknüpfen.", "Este PDF vinculado no está disponible en este dispositivo. Abre la biblioteca de PDF para volver a vincularlo.", "연결된 PDF를 이 기기에서 사용할 수 없습니다. PDF 라이브러리에서 다시 연결하세요.", "Este PDF vinculado não está disponível neste dispositivo. Abra a biblioteca de PDFs para vinculá-lo novamente.", "Ce PDF lié n’est pas disponible sur cet appareil. Ouvrez la bibliothèque PDF pour le relier.", "PDF được liên kết không có trên thiết bị này. Mở thư viện PDF để liên kết lại.", "此设备上没有该关联 PDF。请打开 PDF 库重新链接。", "यह लिंक किया गया PDF इस डिवाइस पर उपलब्ध नहीं है। इसे फिर से लिंक करने के लिए PDF लाइब्रेरी खोलें।"),
    ("Could not open the linked PDF.", "Die verknüpfte PDF konnte nicht geöffnet werden.", "No se pudo abrir el PDF vinculado.", "연결된 PDF를 열 수 없습니다.", "Não foi possível abrir o PDF vinculado.", "Impossible d’ouvrir le PDF lié.", "Không thể mở PDF được liên kết.", "无法打开关联的 PDF。", "लिंक किया गया PDF नहीं खोला जा सका।"),
    ("Rendering page {page}…", "Seite {page} wird dargestellt…", "Renderizando la página {page}…", "{page}페이지 렌더링 중…", "Renderizando a página {page}…", "Affichage de la page {page}…", "Đang hiển thị trang {page}…", "正在渲染第 {page} 页…", "पृष्ठ {page} रेंडर हो रहा है…"),
])

_add_rows([
    ("Choose Example Wallpaper", "Beispiel-Wallpaper auswählen", "Elegir fondo de ejemplo", "예시 배경화면 선택", "Escolher papel de parede de exemplo", "Choisir un fond d’écran d’exemple", "Chọn hình nền mẫu", "选择示例壁纸", "उदाहरण वॉलपेपर चुनें"),
    ("Example Wallpapers", "Beispiel-Wallpaper", "Fondos de ejemplo", "예시 배경화면", "Papéis de parede de exemplo", "Fonds d’écran d’exemple", "Hình nền mẫu", "示例壁纸", "उदाहरण वॉलपेपर"),
    ("Wallpaper file not available yet.", "Die Wallpaper-Datei ist noch nicht verfügbar.", "El archivo del fondo aún no está disponible.", "배경화면 파일을 아직 사용할 수 없습니다.", "O arquivo do papel de parede ainda não está disponível.", "Le fichier du fond d’écran n’est pas encore disponible.", "Tệp hình nền chưa có sẵn.", "壁纸文件尚不可用。", "वॉलपेपर फ़ाइल अभी उपलब्ध नहीं है।"),
    ("Use Wallpaper", "Wallpaper verwenden", "Usar fondo", "배경화면 사용", "Usar papel de parede", "Utiliser ce fond d’écran", "Dùng hình nền", "使用壁纸", "वॉलपेपर उपयोग करें"),
    ("Light Wallpaper", "Helles Wallpaper", "Fondo claro", "밝은 배경화면", "Papel de parede claro", "Fond d’écran clair", "Hình nền sáng", "浅色壁纸", "हल्का वॉलपेपर"),
    ("A bright wallpaper designed for Light Mode.", "Ein helles Wallpaper, das für den hellen Modus gestaltet wurde.", "Un fondo luminoso diseñado para el modo claro.", "라이트 모드용으로 디자인된 밝은 배경화면입니다.", "Um papel de parede claro criado para o modo claro.", "Un fond d’écran lumineux conçu pour le mode clair.", "Hình nền sáng được thiết kế cho chế độ sáng.", "专为浅色模式设计的明亮壁纸。", "लाइट मोड के लिए बनाया गया हल्का वॉलपेपर।"),
    ("Dark Wallpaper", "Dunkles Wallpaper", "Fondo oscuro", "어두운 배경화면", "Papel de parede escuro", "Fond d’écran sombre", "Hình nền tối", "深色壁纸", "गहरा वॉलपेपर"),
    ("A dark wallpaper designed for Dark Mode.", "Ein dunkles Wallpaper, das für den dunklen Modus gestaltet wurde.", "Un fondo oscuro diseñado para el modo oscuro.", "다크 모드용으로 디자인된 어두운 배경화면입니다.", "Um papel de parede escuro criado para o modo escuro.", "Un fond d’écran sombre conçu pour le mode sombre.", "Hình nền tối được thiết kế cho chế độ tối.", "专为深色模式设计的深色壁纸。", "डार्क मोड के लिए बनाया गया गहरा वॉलपेपर।"),
    ("Abstract Wallpaper", "Abstraktes Wallpaper", "Fondo abstracto", "추상 배경화면", "Papel de parede abstrato", "Fond d’écran abstrait", "Hình nền trừu tượng", "抽象壁纸", "अमूर्त वॉलपेपर"),
    ("A colorful abstract wallpaper suitable for either mode.", "Ein farbenfrohes abstraktes Wallpaper, das für beide Modi geeignet ist.", "Un fondo abstracto y colorido adecuado para ambos modos.", "두 모드 모두에 어울리는 다채로운 추상 배경화면입니다.", "Um papel de parede abstrato e colorido adequado para ambos os modos.", "Un fond d’écran abstrait et coloré adapté aux deux modes.", "Hình nền trừu tượng nhiều màu phù hợp với cả hai chế độ.", "适用于两种模式的彩色抽象壁纸。", "दोनों मोड के लिए उपयुक्त रंगीन अमूर्त वॉलपेपर।"),
])

_add_rows([
    ('Basic', 'Grundeinstellungen', 'Básico', '기본', 'Básico', 'Général', 'Cơ bản', '基本', 'मूल'),
    ('Layout', 'Darstellung', 'Diseño', '레이아웃', 'Layout', 'Affichage', 'Bố cục', '布局', 'लेआउट'),
    ('Standard', 'Standard', 'Estándar', '표준', 'Padrão', 'Standard', 'Tiêu chuẩn', '标准', 'मानक'),
])

_add_rows([
    ('Card type', 'Kartentyp', 'Tipo de tarjeta', '카드 유형', 'Tipo de cartão', 'Type de carte', 'Loại thẻ', '卡片类型', 'कार्ड का प्रकार'),
    ('Basic + Reversed', 'Basic + umgekehrt', 'Básica + invertida', '기본 + 역방향', 'Básico + invertido', 'Basique + inversée', 'Cơ bản + đảo ngược', '基础 + 反向', 'मूल + उल्टा'),
    ('Cloze', 'Lückentext', 'Texto con huecos', '빈칸', 'Lacunas', 'Texte à trous', 'Điền khuyết', '填空', 'रिक्त स्थान'),
    ('New cloze', 'Neue Lücke', 'Nuevo hueco', '새 빈칸', 'Nova lacuna', 'Nouveau trou', 'Chỗ trống mới', '新建填空', 'नया रिक्त स्थान'),
    ('Same card', 'Gleiche Karte', 'Misma tarjeta', '같은 카드', 'Mesmo cartão', 'Même carte', 'Cùng thẻ', '同一卡片', 'वही कार्ड'),
    ('Text', 'Text', 'Texto', '텍스트', 'Texto', 'Texte', 'Văn bản', '文本', 'पाठ'),
    ('Extra', 'Zusatz', 'Extra', '추가', 'Extra', 'Complément', 'Bổ sung', '补充', 'अतिरिक्त'),
    ('Select text below, then add a cloze. Different numbers create separate cards; matching numbers hide together.', 'Markiere unten Text und füge eine Lücke hinzu. Verschiedene Nummern erzeugen separate Karten; gleiche Nummern werden gemeinsam ausgeblendet.', 'Selecciona texto abajo y añade un hueco. Los números distintos crean tarjetas separadas; los iguales se ocultan juntos.', '아래 텍스트를 선택하고 빈칸을 추가하세요. 다른 번호는 별도 카드를 만들고, 같은 번호는 함께 숨겨집니다.', 'Selecione o texto abaixo e adicione uma lacuna. Números diferentes criam cartões separados; números iguais são ocultados juntos.', 'Sélectionnez du texte ci-dessous et ajoutez un trou. Des numéros différents créent des cartes séparées ; les numéros identiques sont masqués ensemble.', 'Chọn văn bản bên dưới rồi tạo chỗ trống. Số khác nhau tạo thẻ riêng; số giống nhau được ẩn cùng lúc.', '选择下方文本后添加填空。不同编号生成独立卡片，相同编号会一起隐藏。', 'नीचे पाठ चुनें, फिर रिक्त स्थान जोड़ें। अलग संख्याएँ अलग कार्ड बनाती हैं; समान संख्याएँ एक साथ छिपती हैं।'),
    ('Select the text you want to hide first.', 'Markiere zuerst den Text, den du ausblenden möchtest.', 'Primero selecciona el texto que quieres ocultar.', '먼저 숨길 텍스트를 선택하세요.', 'Primeiro selecione o texto que deseja ocultar.', 'Sélectionnez d’abord le texte à masquer.', 'Trước tiên hãy chọn văn bản muốn ẩn.', '请先选择要隐藏的文本。', 'पहले वह पाठ चुनें जिसे छिपाना है।'),
    ('Select plain text outside an existing cloze.', 'Markiere normalen Text außerhalb einer vorhandenen Lücke.', 'Selecciona texto fuera de un hueco existente.', '기존 빈칸 밖의 일반 텍스트를 선택하세요.', 'Selecione texto fora de uma lacuna existente.', 'Sélectionnez du texte en dehors d’un trou existant.', 'Chọn văn bản nằm ngoài chỗ trống hiện có.', '请选择已有填空之外的普通文本。', 'मौजूदा रिक्त स्थान के बाहर का सामान्य पाठ चुनें।'),
    ('Add at least one cloze deletion, for example {{c1::answer}}.', 'Füge mindestens eine Lücke ein, zum Beispiel {{c1::Antwort}}.', 'Añade al menos un hueco, por ejemplo {{c1::respuesta}}.', '빈칸을 하나 이상 추가하세요. 예: {{c1::답}}.', 'Adicione pelo menos uma lacuna, por exemplo {{c1::resposta}}.', 'Ajoutez au moins un trou, par exemple {{c1::réponse}}.', 'Thêm ít nhất một chỗ trống, ví dụ {{c1::đáp án}}.', '请至少添加一个填空，例如 {{c1::答案}}。', 'कम से कम एक रिक्त स्थान जोड़ें, जैसे {{c1::उत्तर}}।'),
    ('Reversed cards need text on both sides.', 'Umgekehrte Karten benötigen Text auf beiden Seiten.', 'Las tarjetas invertidas necesitan texto en ambos lados.', '역방향 카드는 양쪽에 텍스트가 필요합니다.', 'Cartões invertidos precisam de texto nos dois lados.', 'Les cartes inversées nécessitent du texte des deux côtés.', 'Thẻ đảo ngược cần văn bản ở cả hai mặt.', '反向卡片的两面都需要文本。', 'उल्टे कार्ड के दोनों ओर पाठ होना चाहिए।'),
])

_add_rows([('Basic (Front / Back)', 'Basic (Vorder- / Rückseite)', 'Básica (anverso / reverso)', '기본 (앞면 / 뒷면)', 'Básico (frente / verso)', 'Basique (recto / verso)', 'Cơ bản (mặt trước / sau)', '基础（正面 / 背面）', 'मूल (आगे / पीछे)')])


WEB_TRANSLATIONS.update({
    "Widget Shadow": {
        "de": "Widget-Schatten", "es": "Sombra de widgets", "ko": "위젯 그림자",
        "pt": "Sombra dos widgets", "fr": "Ombre des widgets", "vi": "Bóng tiện ích",
        "zh": "组件阴影", "hi": "विजेट की छाया", "pl": "Cień widżetów",
    },
    "Shadow intensity for widgets and the deck list. Set to 0 to turn off.": {
        "de": "Schattenstärke für Widgets und Stapelliste. Zum Ausschalten auf 0 setzen.",
        "es": "Intensidad de sombra para widgets y lista de mazos. Pon 0 para desactivarla.",
        "ko": "위젯과 덱 목록의 그림자 강도입니다. 0으로 설정하면 꺼집니다.",
        "pt": "Intensidade da sombra dos widgets e da lista de baralhos. Use 0 para desativar.",
        "fr": "Intensité de l’ombre des widgets et de la liste des paquets. Réglez sur 0 pour désactiver.",
        "vi": "Độ đậm bóng của tiện ích và danh sách bộ thẻ. Đặt 0 để tắt.",
        "zh": "组件和牌组列表的阴影强度。设为 0 可关闭。",
        "hi": "विजेट और डेक सूची की छाया की तीव्रता। बंद करने के लिए 0 चुनें।",
        "pl": "Intensywność cienia widżetów i listy talii. Ustaw 0, aby wyłączyć.",
    },
})
