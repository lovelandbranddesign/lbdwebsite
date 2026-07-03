#!/usr/bin/env python3
"""
LBD Build Script
Reads markdown posts from /posts, generates HTML for any post
where publish_date <= today. Regenerates the insights hub.
Run by Netlify on every deploy.
"""

import os, re, datetime
import markdown
import yaml

TODAY = datetime.date.today()
POSTS_DIR = 'posts'
INSIGHTS_DIR = 'insights'

os.makedirs(INSIGHTS_DIR, exist_ok=True)

# ── GTM (stored as variables so f-strings don't break) ──
GTM_HEAD = ('<!-- Google Tag Manager -->'
    '<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({"gtm.start":'
    'new Date().getTime(),event:"gtm.js"});var f=d.getElementsByTagName(s)[0],'
    'j=d.createElement(s),dl=l!="dataLayer"?"&l="+l:"";j.async=true;j.src='
    '"https://www.googletagmanager.com/gtm.js?id="+i+dl;f.parentNode.insertBefore(j,f);'
    '})(window,document,"script","dataLayer","GTM-N9TJVTCR");</script>'
    '<!-- End Google Tag Manager -->')

GTM_BODY = ('<!-- Google Tag Manager (noscript) -->'
    '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N9TJVTCR"'
    ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
    '<!-- End Google Tag Manager (noscript) -->')

NETLIFY_ID = '<script src="https://identity.netlify.com/v1/netlify-identity-widget.js"></script>'

# ── Shared components ──
def get_base_css():
    try:
        with open('about.html', 'r') as f:
            html = f.read()
        m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
        if m:
            return m.group(1)
    except:
        pass
    return ""

TICKER = """<div class="ticker" aria-hidden="true"><div class="ticker-track">
<span class="ticker-item">Custom Strategy</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">Fixed Scope</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">No Hourly Billing</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">AI-Integrated Growth</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">Systems That Give You Your Bandwidth Back</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">Business Owners Shouldn't Have to Become Marketers</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">Custom Strategy</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">Fixed Scope</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">AI-Integrated Growth</span><span class="ticker-sep">&nbsp;·&nbsp;</span>
<span class="ticker-item">Systems That Give You Your Bandwidth Back</span>
</div></div>"""

NAV = """<nav id="mainNav"><div class="nav-inner">
  <a href="/" class="nav-logo-svg">
    <span class="nav-logo-wordmark">LOVELAND<span class="nav-logo-dot">.</span></span>
    <span class="nav-logo-sub">Brand Design</span>
  </a>
  <ul class="nav-links">
    <li><a href="/about">About</a></li>
    <li><a href="/work">Our Work</a></li>
    <li class="nav-dropdown">
      <a href="/solutions">Solutions</a>
      <div class="nav-drop-menu">
        <span class="nav-drop-label">Seven Movements</span>
        <a href="/solutions/marketing-action-plan" class="nav-drop-item">Marketing Action Plan</a>
        <a href="/solutions/brand-architecture" class="nav-drop-item">Brand Architecture</a>
        <a href="/solutions/digital-ecosystem" class="nav-drop-item">Digital Ecosystem</a>
        <a href="/solutions/marketing-operations" class="nav-drop-item">Marketing Operations</a>
        <a href="/solutions/content-and-social" class="nav-drop-item">Content and Social</a>
        <a href="/solutions/prospecting-and-pipeline" class="nav-drop-item">Prospecting and Pipeline</a>
        <a href="/solutions/digital-advertising" class="nav-drop-item">Digital Advertising</a>
        <div class="nav-drop-divider"></div>
        <a href="/solutions" class="nav-drop-item accent">View All Solutions</a>
      </div>
    </li>
    <li class="nav-dropdown">
      <a href="/insights" class="active">Resources</a>
      <div class="nav-drop-menu">
        <a href="/insights" class="nav-drop-item">Insights</a>
        <a href="/faqs" class="nav-drop-item">FAQs</a>
        <a href="/12-pillars-of-digital-marketing-health" class="nav-drop-item">12 Pillars</a>
        <div class="nav-drop-divider"></div>
        <a href="/eky" class="nav-drop-item">Eastern Kentucky</a>
      </div>
    </li>
    <li><a href="/approach">Approach</a></li>
    <li><a href="/contact">Contact</a></li>
    <li><span class="nav-phone">617.686.5618</span></li>
  </ul>
  <button class="nav-burger" id="navBurger" aria-label="Open menu"><span></span><span></span><span></span></button>
  <a href="/contact" class="nav-cta">Start My MAP</a>
</div></nav>"""

FOOTER = """<footer><div class="container">
  <div class="footer-grid">
    <div>
      <div class="footer-logo-svg">
        <span class="footer-logo-wordmark">LOVELAND<span class="footer-logo-dot">.</span></span>
        <span class="footer-logo-sub">Brand Design</span>
      </div>
      <p class="footer-tagline">AI-powered marketing systems for businesses doing work worth defending.</p>
      <div class="footer-contact">
        <a href="tel:6176865618">617.686.5618</a>
        <a href="mailto:info@lovelandbranddesign.com">info@lovelandbranddesign.com</a>
        <a href="#">Pikeville, Kentucky</a>
      </div>
    </div>
    <div class="footer-col">
      <div class="footer-col-label">Solutions</div>
      <ul>
        <li><a href="/solutions/marketing-action-plan">Marketing Action Plan</a></li>
        <li><a href="/solutions/brand-architecture">Brand Architecture</a></li>
        <li><a href="/solutions/digital-ecosystem">Digital Ecosystem</a></li>
        <li><a href="/solutions/marketing-operations">Marketing Operations</a></li>
        <li><a href="/solutions/content-and-social">Content and Social</a></li>
        <li><a href="/solutions/prospecting-and-pipeline">Prospecting and Pipeline</a></li>
        <li><a href="/solutions/digital-advertising">Digital Advertising</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <div class="footer-col-label">Company</div>
      <ul>
        <li><a href="/about">About</a></li>
        <li><a href="/approach">Approach</a></li>
        <li><a href="/work">Our Work</a></li>
        <li><a href="/faqs">FAQs</a></li>
        <li><a href="/insights">Insights</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <div class="footer-col-label">Start Here</div>
      <ul>
        <li><a href="/contact">Start My MAP</a></li>
        <li><a href="mailto:info@lovelandbranddesign.com">Send an Email</a></li>
        <li><a href="tel:6176865618">Call Us</a></li>
        <li><a href="/privacy">Privacy Policy</a></li>
        <li><a href="/terms">Terms of Service</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="footer-copy">© 2026 Loveland Brand Design LLC. Pikeville, Kentucky.</div>
    <ul class="footer-values"><li>Simplicity</li><li>Systems</li><li>Fit</li><li>Freedom</li><li>Honesty</li></ul>
  </div>
</div></footer>"""

JS = """<script>
// Scroll nav
const nav=document.getElementById('mainNav');
if(nav) window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>80);},{passive:true});
// Reveal
const io=new IntersectionObserver((e)=>{e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('visible');io.unobserve(x.target);}});},{threshold:.1,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
// FAQ accordion
document.querySelectorAll('.faq-q').forEach(q=>{q.addEventListener('click',()=>{q.parentElement.classList.toggle('open');});});
// Mobile burger
const burger=document.getElementById('navBurger');
const navLinks=document.querySelector('.nav-links');
if(burger&&navLinks){
  burger.addEventListener('click',()=>{burger.classList.toggle('open');navLinks.classList.toggle('open');});
  navLinks.querySelectorAll('a:not(.nav-drop-item)').forEach(a=>{a.addEventListener('click',()=>{burger.classList.remove('open');navLinks.classList.remove('open');});});
}
// Dropdown nav — click-based for reliability
document.querySelectorAll('.nav-dropdown > a').forEach(function(trigger){
  trigger.addEventListener('click',function(e){
    var isMobile = window.innerWidth <= 768;
    if(!isMobile){
      e.preventDefault(); e.stopPropagation();
      var menu = this.nextElementSibling;
      var isOpen = menu.classList.contains('open');
      document.querySelectorAll('.nav-drop-menu').forEach(function(m){m.classList.remove('open');});
      if(!isOpen) menu.classList.add('open');
    }
  });
});
document.addEventListener('click',function(e){
  if(!e.target.closest('.nav-dropdown')){
    document.querySelectorAll('.nav-drop-menu').forEach(function(m){m.classList.remove('open');});
  }
});
// Netlify Identity
if(window.netlifyIdentity){window.netlifyIdentity.on('init',function(u){if(!u){window.netlifyIdentity.on('login',function(){document.location.href='/admin/';});}});}
</script>"""

# ── Parse frontmatter ──
def parse_post(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()
    fm_match = re.match(r'^---\n(.*?)\n---\n(.*)', raw, re.DOTALL)
    if not fm_match:
        return None
    try:
        meta = yaml.safe_load(fm_match.group(1))
        body_md = fm_match.group(2).strip()
    except:
        return None
    pub_date = meta.get('publish_date')
    if isinstance(pub_date, str):
        try:
            pub_date = datetime.date.fromisoformat(pub_date)
        except:
            return None
    elif isinstance(pub_date, datetime.datetime):
        pub_date = pub_date.date()
    if not pub_date:
        return None
    slug = os.path.basename(filepath).replace('.md', '')
    return {
        'title': meta.get('title', 'Untitled'),
        'publish_date': pub_date,
        'category': meta.get('category', 'Insights'),
        'excerpt': meta.get('excerpt', ''),
        'featured_image': meta.get('featured_image', ''),
        'seo_title': meta.get('seo_title') or meta.get('title', 'Untitled'),
        'seo_description': meta.get('seo_description') or meta.get('excerpt', ''),
        'body_html': markdown.markdown(body_md, extensions=['extra', 'nl2br']),
        'slug': slug,
        'url': '/insights/' + slug,
    }

# ── Generate post page ──
def generate_post_page(post, css):
    date_str = post['publish_date'].strftime('%B %d, %Y')
    featured = ''
    if post['featured_image']:
        featured = '<div style="margin-bottom:48px;"><img src="' + post['featured_image'] + '" style="width:100%;display:block;" alt="' + post['title'] + '"></div>'
    body = ('<section class="page-header teal-dark">'
        '<div class="container ph-max">'
        '<div class="eyebrow ew-gold reveal">' + post['category'] + '</div>'
        '<h1 class="page-heading reveal">' + post['title'] + '</h1>'
        '<div style="margin-top:20px;font-family:var(--font-display);font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.4);">' + date_str + '</div>'
        '</div></section>'
        '<section class="s-dark"><div class="container"><div class="sidebar-left">'
        '<div class="reveal"><div style="position:sticky;top:calc(var(--ticker-h) + var(--nav-h) + 32px);">'
        '<div style="font-family:var(--font-display);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--mid-grey);margin-bottom:20px;">In This Post</div>'
        '<div style="font-size:14px;line-height:1.75;color:rgba(245,245,245,.45);margin-bottom:32px;">' + post['excerpt'] + '</div>'
        '<a href="/insights" style="font-family:var(--font-display);font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--teal-light);">← All Insights</a>'
        '<div style="margin-top:48px;padding-top:40px;border-top:1px solid rgba(245,245,245,.08);">'
        '<a href="/contact" class="btn-primary" style="display:block;text-align:center;">Start My MAP</a>'
        '</div></div></div>'
        '<div class="reveal">' + featured + '<div class="post-body prose" style="max-width:none;">' + post['body_html'] + '</div>'
        '<div style="margin-top:64px;padding-top:40px;border-top:1px solid rgba(245,245,245,.08);">'
        '<div class="eyebrow ew-orange">Ready to build?</div>'
        '<h2 class="section-heading" style="font-size:clamp(28px,3vw,42px);margin-bottom:16px;">Every engagement starts with the MAP.</h2>'
        '<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        '<a href="/contact" class="btn-primary">Start My MAP</a>'
        '<a href="/insights" class="btn-ghost">More Insights</a>'
        '</div></div></div></div></div></section>')

    post_css = (css +
        '.post-body h2{font-family:var(--font-display);font-size:clamp(24px,3vw,36px);font-weight:900;text-transform:uppercase;color:var(--beige);margin:48px 0 16px;}'
        '.post-body h3{font-family:var(--font-display);font-size:clamp(18px,2vw,24px);font-weight:800;text-transform:uppercase;color:var(--beige);margin:36px 0 12px;}'
        '.post-body p{font-size:16px;line-height:1.8;color:rgba(245,245,245,.7);margin-bottom:20px;}'
        '.post-body strong{color:var(--beige);font-weight:500;}'
        '.post-body ul,.post-body ol{margin:0 0 20px 20px;color:rgba(245,245,245,.7);font-size:16px;line-height:1.8;}'
        '.post-body li{margin-bottom:8px;}'
        '.post-body blockquote{border-left:3px solid var(--orange);padding-left:24px;margin:32px 0;}'
        '.post-body blockquote p{color:rgba(245,245,245,.85);font-size:17px;}'
        '.post-body a{color:var(--teal-light);text-decoration:underline;}'
        '.post-body hr{border:none;border-top:1px solid rgba(245,245,245,.08);margin:48px 0;}')

    return ('<!DOCTYPE html><html lang="en"><head>' +
        GTM_HEAD +
        NETLIFY_ID +
        '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>' + post['seo_title'] + ' | Loveland Brand Design</title>'
        '<meta name="description" content="' + post['seo_description'] + '">'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">'
        '<style>' + post_css + '</style>'
        '</head><body>' +
        GTM_BODY + TICKER + NAV + body + FOOTER + JS +
        '</body></html>')

# ── Generate insights hub ──
def generate_insights_hub(published_posts, css):
    if published_posts:
        cards = ''
        for post in sorted(published_posts, key=lambda p: p['publish_date'], reverse=True):
            date_str = post['publish_date'].strftime('%B %d, %Y')
            cards += ('<a href="' + post['url'] + '" class="insight-card">'
                '<div class="insight-cat">' + post['category'] + '</div>'
                '<div class="insight-title">' + post['title'] + '</div>'
                '<p class="insight-excerpt">' + post['excerpt'] + '</p>'
                '<div class="insight-meta">' + date_str + '</div>'
                '</a>')
        grid = '<div class="insight-grid">' + cards + '</div>'
    else:
        grid = ('<div class="placeholder-block" style="margin-top:56px;">'
            '<div class="placeholder-label">Insights — Coming Soon</div>'
            '<p class="placeholder-text">Articles, frameworks, and honest takes on what works in marketing for businesses doing real work.</p>'
            '</div>')

    body = ('<section class="page-header"><div class="container ph-max">'
        '<div class="eyebrow ew-teal reveal">Insights</div>'
        '<h1 class="page-heading reveal">What we know.<br><span class="at">What we\'ve learned.</span><br>What you can use.</h1>'
        '<p class="page-sub reveal">Strategy frameworks, system thinking, and honest takes on what works in marketing for businesses doing real work.</p>'
        '</div></section>'
        '<section class="s-darker"><div class="container reveal">' + grid + '</div></section>'
        '<div class="cta-band"><div class="container">'
        '<h2 class="cta-band-heading">Ready to start building?</h2>'
        '<p class="cta-band-sub">The MAP is where it starts. Strategy before execution, every time.</p>'
        '<div class="cta-band-actions">'
        '<a href="/contact" class="btn-white">Start My MAP</a>'
        '<a href="/faqs" class="btn-ghost" style="border-color:rgba(255,255,255,.35);color:var(--white);">Read the FAQs</a>'
        '</div></div></div>')

    return ('<!DOCTYPE html><html lang="en"><head>' +
        GTM_HEAD + NETLIFY_ID +
        '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>Insights | Loveland Brand Design</title>'
        '<meta name="description" content="Strategy frameworks, system thinking, and honest takes on what works in marketing for businesses doing real work.">'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">'
        '<style>' + css + '</style>'
        '</head><body>' +
        GTM_BODY + TICKER + NAV + body + FOOTER + JS +
        '</body></html>')

# ── Main ──
def main():
    css = get_base_css()
    published = []
    if os.path.exists(POSTS_DIR):
        for fname in os.listdir(POSTS_DIR):
            if not fname.endswith('.md'):
                continue
            post = parse_post(os.path.join(POSTS_DIR, fname))
            if not post:
                continue
            if post['publish_date'] <= TODAY:
                html = generate_post_page(post, css)
                out = os.path.join(INSIGHTS_DIR, post['slug'] + '.html')
                with open(out, 'w', encoding='utf-8') as f:
                    f.write(html)
                published.append(post)
                print('  Published: ' + post['slug'])
            else:
                print('  Scheduled: ' + post['slug'] + ' (' + str(post['publish_date']) + ')')
    hub = generate_insights_hub(published, css)
    with open('insights.html', 'w', encoding='utf-8') as f:
        f.write(hub)
    print('  Hub: insights.html (' + str(len(published)) + ' posts)')
    print('Build complete.')

if __name__ == '__main__':
    main()
