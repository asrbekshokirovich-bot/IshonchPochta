// copy.jsx — all i18n strings for Ishonch Logistics
// Languages: uz (Uzbek Latin), ru (Russian), en (English)

const COPY = {
  uz: {
    nav: { services: "Xizmatlar", coverage: "Hududlar", calc: "Hisoblash", about: "Biz haqimizda", contact: "Aloqa" },
    top: { phone: "Qo'llab-quvvatlash: 71 200 22 22", hours: "24/7 ish vaqti", track: "Yukni kuzatish" },
    actions: { track: "Yukni kuzatish", order: "Buyurtma berish", quote: "Narxni hisoblash", call: "Bog'lanish" },
    hero: {
      tag: "ISHONCHLI",
      tagAlt: "1 yetkazib berish — 24 soatda",
      title: ["O'zbekiston bo'ylab", "ishonchli yetkazib", "berish xizmati"],
      titleAccent: "ishonchli yetkazib",
      lede: "Toshkentdan Termizgacha — har bir paket o'z vaqtida, narxi shaffof, kuzatuv har bir bekatda. Kichik biznes va oddiy odamlar uchun arzon tariflar.",
      script: "Ishonch har bir yetkazishda",
      stats: [
        { n: "14", l: "Viloyat" },
        { n: "180+", l: "Bekat" },
        { n: "24 soat", l: "O'rtacha vaqt" }
      ]
    },
    trustLabel: "Bizga ishonadigan kompaniyalar",
    services: {
      eyebrow: "XIZMATLAR",
      title: "Har bir holatga to'g'ri keladigan yechim",
      meta: "Hujjatdan tortib yirik yukgacha — sizning ehtiyojingizga qarab tezkor yoki tejamkor variantni tanlang.",
      items: [
        { ico: "express", name: "Tezkor yetkazish", desc: "Toshkent ichida 3 soatda, viloyatga shu kuni jo'natish.", price: "15 000 so'mdan" },
        { ico: "standard", name: "Standart", desc: "1–2 ish kuni ichida butun mamlakat bo'ylab eng arzon tarif.", price: "8 000 so'mdan", featured: true },
        { ico: "cargo", name: "Yuk va kargo", desc: "100 kg gacha. Yuklash, mahkamlash va sug'urta — bizning zimmamizda.", price: "Hisobga ko'ra" },
        { ico: "intl", name: "Xalqaro", desc: "Rossiya, Qozog'iston, Xitoy va Turkiya yo'nalishlari, bojxona ko'magi.", price: "$9'dan" },
        { ico: "cod", name: "Naqd to'lov", desc: "Mijoz qabul qilganda to'lashi mumkin — onlayn-do'konlar uchun ideal.", price: "0% komissiya" },
        { ico: "ecom", name: "Onlayn-do'kon", desc: "Telegram va Instagram do'konlari uchun ombor, qadoqlash va yetkazish.", price: "Paketda" }
      ]
    },
    why: {
      eyebrow: "NEGA AYNAN BIZ",
      title: "Soddalik, tezlik va shaffof narx — bir joyda",
      items: [
        { ico: "wallet",  h: "Eng arzon tarif",   p: "Boshlang'ich narx 8 000 so'mdan. Hech qanday yashirin to'lov yo'q." },
        { ico: "clock",   h: "O'z vaqtida",       p: "Yetkazib berishning 96% i va'da qilingan muddat ichida amalga oshadi." },
        { ico: "map",     h: "Har bir tumanda",   p: "180 dan ortiq bekat — qishloqlargacha yetib boramiz." },
        { ico: "shield",  h: "1 mln so'mgacha sug'urta", p: "Har bir yuk avtomatik tarzda sug'urtalanadi. Tinch yuring." }
      ],
      stats: [
        { n: "1.4M", l: "Yiliga yetkazilgan paket" },
        { n: "96%", l: "Vaqtida yetkazib berish" }
      ]
    },
    coverage: {
      eyebrow: "QAMROV HUDUDI",
      title: "O'zbekistonning har bir burchagiga yetib boramiz",
      meta: "Toshkentdan Buxoro, Xivagacha — qishloq joylar ham qoldi degan gap yo'q. Yangi viloyat ochilganida, sizga avval xabar beramiz.",
      pts: [
        "14 viloyat va Qoraqalpog'iston bo'ylab",
        "180+ qabul va topshirish bekati",
        "Eshikma-eshik xizmati Toshkentda bepul"
      ]
    },
    calc: {
      eyebrow: "TEZKOR HISOB",
      title: "Yukingizni 10 soniyada hisoblang",
      meta: "Qayerdan, qayerga, og'irligi qancha — narx darhol ko'rinadi. Hech qachon yashirin to'lov yo'q.",
      from: "Qayerdan", to: "Qayerga", weight: "Og'irlik (kg)", service: "Xizmat turi",
      total: "Taxminiy narx",
      sub: "Sug'urta va eshikma-eshik xizmati narxga kiritilgan",
      cta: "Buyurtma berish"
    },
    steps: {
      eyebrow: "QANDAY ISHLAYDI",
      title: "4 oddiy qadam",
      items: [
        { h: "Buyurtma bering",   p: "Saytdan, ilovadan yoki qo'ng'iroq orqali — 1 daqiqada." },
        { h: "Biz olib ketamiz",   p: "Kuryer eshigingizgacha keladi. Toshkentda bepul." },
        { h: "Yo'ldagi yukni kuzating", p: "Har bir bekatda SMS va ilova orqali yangilik oling." },
        { h: "Yetkazib beriladi",  p: "Qabul qiluvchi imzo qo'yadi va sizga avtomatik xabar keladi." }
      ]
    },
    testimonials: {
      eyebrow: "MIJOZLAR FIKRI",
      title: "Bizga ishonganlar so'zi",
      items: [
        { quote: "Onlayn-do'konimiz uchun har kuni 40-50 ta buyurtmani yetkazadi. Hech qachon kechikkan emas, mijozlarim mamnun.",
          name: "Dilshoda Karimova", role: "Asal Beauty, Toshkent" },
        { quote: "Termizdagi onamga doriyu shifo yuborish endi 2 kun emas, 1 kechada yetib boradi. Va narxi taksi puli bilan deyarli bir xil.",
          name: "Sherzod Tursunov", role: "Mijoz, Toshkent" },
        { quote: "Yuk yo'qolib ketdi degan tashvish yo'q. Sug'urta avtomat — bir marta zarur bo'lganda, 2 kun ichida zarar qoplandi.",
          name: "Aziza Yusupova", role: "Texno do'koni egasi" }
      ]
    },
    cta: {
      title: "Bugun buyurtma bersangiz, ertaga yetkazamiz",
      lede: "Telefon raqamingizni qoldiring — operatorimiz 5 daqiqada bog'lanadi va eshigingizdan yukni olib ketadi.",
      name: "Ismingiz", phone: "Telefon raqami", city: "Shahar",
      btn: "Kuryer chaqirish",
      note: "Yoki to'g'ridan-to'g'ri qo'ng'iroq qiling: 71 200 22 22"
    },
    footer: {
      about: "Ishonch Logistics — O'zbekistonning ishonchli yetkazib berish xizmati. 2019-yildan beri har bir yukni o'z manziliga vaqtida olib boramiz.",
      services: "Xizmatlar", company: "Kompaniya", help: "Yordam",
      links: {
        services: ["Tezkor", "Standart", "Yuk va kargo", "Xalqaro", "Naqd to'lov", "Onlayn-do'kon paketi"],
        company:  ["Biz haqimizda", "Bekatlar", "Karyera", "Matbuot", "Hamkorlik"],
        help:     ["Yukni kuzatish", "Narx hisoblash", "Tez-tez beriladigan savollar", "Aloqa", "Shartlar"]
      },
      copyright: "© 2026 Ishonch Logistics MChJ. Barcha huquqlar himoyalangan."
    },
    tracking: {
      placeholder: "Kuzatuv raqami (TN12345678)",
      cta: "Topish",
      sample: "Sinab ko'ring: TN12345678",
      result: { title: "Yukingiz harakatda", body: "Samarqand tarmoq markazidan chiqdi. Toshkentga 6 soat ichida yetadi." },
      tab1: "Yukni kuzatish", tab2: "Buyurtma berish"
    },
    bookForm: {
      fromCity: "Qayerdan (shahar)", toCity: "Qayerga (shahar)",
      pkg: "Yuk turi", weight: "Og'irlik (kg)",
      cta: "Davom etish"
    }
  },

  ru: {
    nav: { services: "Услуги", coverage: "Регионы", calc: "Расчёт", about: "О нас", contact: "Контакты" },
    top: { phone: "Поддержка: 71 200 22 22", hours: "24/7", track: "Отследить" },
    actions: { track: "Отследить", order: "Заказать", quote: "Рассчитать", call: "Связаться" },
    hero: {
      tag: "НАДЁЖНО",
      tagAlt: "Доставка за 24 часа",
      title: ["Надёжная доставка", "по всему", "Узбекистану"],
      titleAccent: "Надёжная доставка",
      lede: "От Ташкента до Термеза — каждая посылка вовремя, цена прозрачная, отслеживание на каждом этапе. Доступные тарифы для малого бизнеса и людей.",
      script: "Доверие в каждой доставке",
      stats: [
        { n: "14", l: "Областей" },
        { n: "180+", l: "Отделений" },
        { n: "24 ч.", l: "Среднее время" }
      ]
    },
    trustLabel: "Нам доверяют",
    services: {
      eyebrow: "УСЛУГИ",
      title: "Решение для любого случая",
      meta: "От документов до крупных грузов — выберите экспресс или экономный тариф под вашу задачу.",
      items: [
        { ico: "express", name: "Экспресс", desc: "По Ташкенту за 3 часа, по областям в тот же день.", price: "от 15 000 сум" },
        { ico: "standard", name: "Стандарт", desc: "1–2 рабочих дня. Самый доступный тариф по стране.", price: "от 8 000 сум", featured: true },
        { ico: "cargo", name: "Карго", desc: "До 100 кг. Погрузка, упаковка и страховка — на нас.", price: "По расчёту" },
        { ico: "intl", name: "Международная", desc: "Россия, Казахстан, Китай, Турция. Помощь с таможней.", price: "от $9" },
        { ico: "cod", name: "Наложенный платёж", desc: "Получатель платит при выдаче — идеально для интернет-магазинов.", price: "0% комиссии" },
        { ico: "ecom", name: "Для онлайн-магазинов", desc: "Склад, упаковка и доставка для Telegram/Instagram магазинов.", price: "Пакет" }
      ]
    },
    why: {
      eyebrow: "ПОЧЕМУ МЫ",
      title: "Просто, быстро, прозрачно — в одном месте",
      items: [
        { ico: "wallet", h: "Самый доступный тариф", p: "От 8 000 сум. Без скрытых платежей." },
        { ico: "clock",  h: "Точно вовремя", p: "96% доставок в обещанный срок." },
        { ico: "map",    h: "В каждом районе", p: "Более 180 отделений — доезжаем даже до посёлков." },
        { ico: "shield", h: "Страховка до 1 млн сум", p: "Каждая посылка автоматически застрахована." }
      ],
      stats: [
        { n: "1.4М", l: "Посылок в год" },
        { n: "96%", l: "Доставок вовремя" }
      ]
    },
    coverage: {
      eyebrow: "ГЕОГРАФИЯ",
      title: "Доезжаем в каждый уголок Узбекистана",
      meta: "От Ташкента до Бухары и Хивы — даже сёла не остаются в стороне. О новых отделениях сообщаем первыми.",
      pts: [
        "14 областей и Каракалпакстан",
        "Более 180 пунктов приёма и выдачи",
        "Бесплатная доставка от двери в Ташкенте"
      ]
    },
    calc: {
      eyebrow: "БЫСТРЫЙ РАСЧЁТ",
      title: "Рассчитайте посылку за 10 секунд",
      meta: "Откуда, куда, сколько кг — цена сразу видна. Никаких скрытых платежей.",
      from: "Откуда", to: "Куда", weight: "Вес (кг)", service: "Тариф",
      total: "Примерная цена",
      sub: "Страховка и доставка от двери включены",
      cta: "Заказать"
    },
    steps: {
      eyebrow: "КАК ЭТО РАБОТАЕТ",
      title: "4 простых шага",
      items: [
        { h: "Сделайте заказ", p: "Через сайт, приложение или по звонку — за 1 минуту." },
        { h: "Курьер заберёт", p: "Приедет к вашей двери. По Ташкенту — бесплатно." },
        { h: "Следите в пути", p: "SMS и уведомления в приложении на каждом этапе." },
        { h: "Доставлено", p: "Получатель расписывается, вам приходит уведомление." }
      ]
    },
    testimonials: {
      eyebrow: "ОТЗЫВЫ",
      title: "Что говорят клиенты",
      items: [
        { quote: "Для нашего интернет-магазина доставляют по 40–50 заказов в день. Ни разу не подвели — клиенты довольны.",
          name: "Дилшода Каримова", role: "Asal Beauty, Ташкент" },
        { quote: "Лекарства маме в Термез теперь идут не 2 дня, а одну ночь. А цена почти как такси.",
          name: "Шерзод Турсунов", role: "Клиент, Ташкент" },
        { quote: "Страх потерять груз ушёл. Страховка автоматом — однажды понадобилась, всё возместили за 2 дня.",
          name: "Азиза Юсупова", role: "Магазин техники" }
      ]
    },
    cta: {
      title: "Закажите сегодня — доставим завтра",
      lede: "Оставьте номер — оператор перезвонит за 5 минут и заберёт посылку у вашей двери.",
      name: "Ваше имя", phone: "Телефон", city: "Город",
      btn: "Вызвать курьера",
      note: "Или позвоните: 71 200 22 22"
    },
    footer: {
      about: "Ishonch Logistics — надёжная служба доставки по Узбекистану. С 2019 года доставляем каждую посылку вовремя.",
      services: "Услуги", company: "Компания", help: "Помощь",
      links: {
        services: ["Экспресс", "Стандарт", "Карго", "Международная", "Наложенный платёж", "Для онлайн-магазинов"],
        company:  ["О нас", "Отделения", "Карьера", "Пресса", "Партнёрство"],
        help:     ["Отследить", "Расчёт цены", "FAQ", "Контакты", "Условия"]
      },
      copyright: "© 2026 ООО Ishonch Logistics. Все права защищены."
    },
    tracking: {
      placeholder: "Номер отслеживания (TN12345678)",
      cta: "Найти",
      sample: "Попробуйте: TN12345678",
      result: { title: "Посылка в пути", body: "Вышла с сортировочного центра в Самарканде. Прибудет в Ташкент через 6 часов." },
      tab1: "Отследить", tab2: "Заказать"
    },
    bookForm: {
      fromCity: "Откуда (город)", toCity: "Куда (город)",
      pkg: "Тип груза", weight: "Вес (кг)",
      cta: "Продолжить"
    }
  },

  en: {
    nav: { services: "Services", coverage: "Coverage", calc: "Pricing", about: "About", contact: "Contact" },
    top: { phone: "Support: 71 200 22 22", hours: "24/7", track: "Track" },
    actions: { track: "Track parcel", order: "Book pickup", quote: "Get a quote", call: "Contact us" },
    hero: {
      tag: "TRUSTED",
      tagAlt: "Next-day delivery",
      title: ["Reliable delivery", "across", "Uzbekistan"],
      titleAccent: "Reliable delivery",
      lede: "From Tashkent to Termez — every parcel on time, transparent pricing, tracking at every stop. Affordable rates for small businesses and individuals.",
      script: "Trust in every delivery",
      stats: [
        { n: "14", l: "Regions" },
        { n: "180+", l: "Branches" },
        { n: "24 hrs", l: "Avg. transit" }
      ]
    },
    trustLabel: "Trusted by",
    services: {
      eyebrow: "SERVICES",
      title: "A solution for every situation",
      meta: "Documents to bulk freight — pick express or economy, whichever fits your need.",
      items: [
        { ico: "express", name: "Express", desc: "Tashkent in 3 hours, regions same-day dispatch.", price: "from 15 000 UZS" },
        { ico: "standard", name: "Standard", desc: "1–2 working days. Cheapest nationwide tariff.", price: "from 8 000 UZS", featured: true },
        { ico: "cargo", name: "Cargo", desc: "Up to 100 kg. Loading, packing and insurance covered.", price: "Quoted" },
        { ico: "intl", name: "International", desc: "Russia, Kazakhstan, China, Turkey. Customs assistance.", price: "from $9" },
        { ico: "cod", name: "Cash on delivery", desc: "Pay-on-receive — ideal for online shops.", price: "0% fee" },
        { ico: "ecom", name: "E-commerce", desc: "Warehouse, packing and last-mile for Telegram/Instagram shops.", price: "Bundle" }
      ]
    },
    why: {
      eyebrow: "WHY US",
      title: "Simple, fast, transparent — all in one place",
      items: [
        { ico: "wallet", h: "Lowest rates",  p: "Starting at 8 000 UZS. Zero hidden fees." },
        { ico: "clock",  h: "On time",        p: "96% of parcels arrive within the promised window." },
        { ico: "map",    h: "Every district", p: "Over 180 branches — we reach the villages too." },
        { ico: "shield", h: "Insurance up to 1M UZS", p: "Every parcel auto-insured. Travel light, sleep tight." }
      ],
      stats: [
        { n: "1.4M", l: "Parcels per year" },
        { n: "96%", l: "On-time rate" }
      ]
    },
    coverage: {
      eyebrow: "COVERAGE",
      title: "We reach every corner of Uzbekistan",
      meta: "Tashkent to Bukhara to Khiva — and the villages in between. New branches announced to you first.",
      pts: [
        "14 regions + Karakalpakstan",
        "180+ pickup & drop-off points",
        "Free door-to-door inside Tashkent"
      ]
    },
    calc: {
      eyebrow: "INSTANT QUOTE",
      title: "Get a price in 10 seconds",
      meta: "From, to, weight — see your price instantly. No hidden charges, ever.",
      from: "From", to: "To", weight: "Weight (kg)", service: "Service",
      total: "Estimated price",
      sub: "Insurance and door-to-door included",
      cta: "Book it"
    },
    steps: {
      eyebrow: "HOW IT WORKS",
      title: "Four simple steps",
      items: [
        { h: "Place an order", p: "On the site, in the app, or by phone — under a minute." },
        { h: "We pick it up", p: "Courier comes to your door. Free in Tashkent." },
        { h: "Track in transit", p: "SMS + in-app updates at every stop." },
        { h: "Delivered", p: "Recipient signs, you get an instant notification." }
      ]
    },
    testimonials: {
      eyebrow: "TESTIMONIALS",
      title: "What our clients say",
      items: [
        { quote: "They handle 40–50 orders a day for our shop. Never late — customers are happy.",
          name: "Dilshoda Karimova", role: "Asal Beauty, Tashkent" },
        { quote: "Sending meds to my mother in Termez used to take 2 days. Now it's one overnight, for taxi-fare prices.",
          name: "Sherzod Tursunov", role: "Customer, Tashkent" },
        { quote: "The fear of losing a shipment is gone. Insurance is automatic — once I needed it, reimbursed in 2 days.",
          name: "Aziza Yusupova", role: "Electronics shop owner" }
      ]
    },
    cta: {
      title: "Order today, delivered tomorrow",
      lede: "Leave your phone — an operator calls back within 5 minutes and picks up your parcel.",
      name: "Your name", phone: "Phone number", city: "City",
      btn: "Request a courier",
      note: "Or call directly: 71 200 22 22"
    },
    footer: {
      about: "Ishonch Logistics — Uzbekistan's reliable delivery service. Since 2019, every parcel on time.",
      services: "Services", company: "Company", help: "Help",
      links: {
        services: ["Express", "Standard", "Cargo", "International", "Cash on delivery", "E-commerce bundle"],
        company:  ["About us", "Branches", "Careers", "Press", "Partners"],
        help:     ["Track parcel", "Pricing", "FAQ", "Contact", "Terms"]
      },
      copyright: "© 2026 Ishonch Logistics LLC. All rights reserved."
    },
    tracking: {
      placeholder: "Tracking number (TN12345678)",
      cta: "Find",
      sample: "Try: TN12345678",
      result: { title: "Your parcel is on the move", body: "Left Samarkand sorting hub. Arrives in Tashkent in 6 hours." },
      tab1: "Track parcel", tab2: "Book pickup"
    },
    bookForm: {
      fromCity: "From (city)", toCity: "To (city)",
      pkg: "Parcel type", weight: "Weight (kg)",
      cta: "Continue"
    }
  }
};

window.COPY = COPY;
