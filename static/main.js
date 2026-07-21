gsap.registerPlugin(ScrollTrigger);

// 🌟 Mobile par GSAP ko band karne ka media query logic
ScrollTrigger.matchMedia({
  
  // 💻 DESKTOP: Agar screen width 769px ya us se zyada hai, toh saari animations chalengi
  "(min-width: 769px)": function() {
    
    const tl = gsap.timeline();

    // 1. Navbar smoothly drop hoga
    tl.fromTo("nav", 
        { opacity: 0, y: -30 }, 
        { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }
    )
    .fromTo("nav #logo", { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, "-=0.3")
    .fromTo("nav a", { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.15, ease: "power2.out" }, "-=0.2")
    .fromTo("nav button", { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, "-=0.2");

    // Section 1
    tl.from("section #left",{ opacity:0, x:-200, duration:1 }, "m4");
    tl.from("section #right",{ opacity:0, x:200, duration:1 }, "m4");

    // Sect 2
    const tl2 = gsap.timeline({
        scrollTrigger:{ trigger:"#features-section", scroller:"body", start: "top 50%", end: "top -70%" }
    });
    tl2.from("#sec2-text",{ opacity:0, x:500, duration:1 });
    tl2.fromTo("#sec2-1", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.3 });
    tl2.fromTo("#sec2-2", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.3 });
    tl2.fromTo("#sec2-3", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.3 });

    // Sect 3: Stats
    const tl3 = gsap.timeline({ scrollTrigger: { trigger: "#stats-section", scroller: "body", start: "top 75%", toggleActions: "play none none none" } });
    tl3.fromTo("#stats-section > div > div", { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.6, stagger: 0.15, ease: "back.out(1.7)" });

    // Sect 4: How It Works
    const tl4 = gsap.timeline({ scrollTrigger: { trigger: "#stats-section + section", scroller: "body", start: "top 90%", toggleActions: "play none none none" } });
    tl4.fromTo("section:has(.step-item) .text-center", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" });
    tl4.fromTo(".step-item", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.25, ease: "power2.out" }, "-=0.2");

    // Stats layout trigger
    const tl5 = gsap.timeline({ scrollTrigger: { trigger: "#stats-section", scroller: "body", start: "top 90%", toggleActions: "play none none none" } });
    tl5.from("#stats-section",{ y:20, opacity:0, duration:1 });

    // Pricing Section
    const tl6 = gsap.timeline({ scrollTrigger: { trigger: "#pricing-section", scroller: "body", start: "top 70%", toggleActions: "play none none none" } });
    tl6.fromTo("#pricing-heading", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" });
    tl6.fromTo(".pricing-card:not(.premium-card)", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.2, ease: "power2.out" }, "-=0.3");
    tl6.fromTo(".pricing-card.premium-card", { opacity: 0, scale: 0.8, y: 40 }, { opacity: 1, scale: 1, duration: 0.8, ease: "back.out(1.5)" }, "-=0.5");

    const tl7 = gsap.timeline({ scrollTrigger: { trigger: "#pricing-section", scroller: "body", start: "top 80%", toggleActions: "play none none none" } });
    tl7.fromTo("#pricing-section h2, #pricing-heading", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" });
    tl7.fromTo(".pricing-card", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.8, stagger: 0.2, ease: "power2.out" }, "-=0.4");

  },

  // 📱 MOBILE: Agar screen size 768px ya us se choti hai, toh koi animation nahi chalegi!
  "(max-width: 768px)": function() {
    // Isko bilkul khali chhor do! Mobile par GSAP ki koi logic fire nahi hogi.
    // Saare elements shuru se hi visible aur static rahenge.
  }

});


// 🍔 MOBILE MENU LOGIC (Yeh hamesha chalega taaki button click ho sake)
const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const menuIcon = document.getElementById('menu-icon');

function toggleMenu(e) {
    e.stopPropagation(); 
    e.preventDefault(); 
    
    mobileMenu.classList.toggle('hidden');
    mobileMenu.classList.toggle('flex');

    if (mobileMenu.classList.contains('hidden')) {
        menuIcon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
    } else {
        menuIcon.setAttribute('d', 'M6 18L18 6M6 6l12 12');
    }
}

menuBtn.addEventListener('touchstart', toggleMenu, { passive: false });
menuBtn.addEventListener('click', toggleMenu);