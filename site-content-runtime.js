(function(){
  'use strict';

  const CONTENT_URL='/site-content.json';
  const byPath=(obj,path)=>String(path).split('.').reduce((value,key)=>value&&Object.prototype.hasOwnProperty.call(value,key)?value[key]:undefined,obj);
  const hasPath=(obj,path)=>byPath(obj,path)!==undefined;
  const text=(node,value)=>{if(node&&value!==undefined&&value!==null)node.textContent=String(value);};
  const money=value=>`${Number(value)||0} zł`;

  function setText(selector,overrides,path){
    if(!hasPath(overrides,path))return;
    text(document.querySelector(selector),byPath(overrides,path));
  }

  function roomCard(id){
    if(id==='tesla')return document.getElementById('escapeboxtesla');
    return document.getElementById(id);
  }

  function applyRoom(overrides,id){
    const prefix=`rooms.${id}`;
    const card=roomCard(id);
    if(!card)return;
    if(hasPath(overrides,`${prefix}.tag`))text(card.querySelector('.pokoj-tag'),byPath(overrides,`${prefix}.tag`));
    if(hasPath(overrides,`${prefix}.description`))text(card.querySelector('.pokoj-desc'),byPath(overrides,`${prefix}.description`));
    if(hasPath(overrides,`${prefix}.priceText`)){
      const price=[...card.querySelectorAll('.pokoj-meta > div')].find(x=>String(x.querySelector('.meta-key')?.textContent||'').trim()==='Cena');
      text(price?.querySelector('.meta-val'),byPath(overrides,`${prefix}.priceText`));
    }
    if(!hasPath(overrides,`${prefix}.status`)&&!hasPath(overrides,`${prefix}.statusText`))return;
    const status=String(byPath(overrides,`${prefix}.status`)||'');
    const statusText=String(byPath(overrides,`${prefix}.statusText`)||'').trim();
    const actions=card.querySelector('.room-actions');
    let badge=card.querySelector('.unavailable-badge');
    if(status==='available'){
      card.classList.remove('is-unavailable','is-coming-soon');
      if(actions)actions.style.display='';
      if(badge)badge.style.display='none';
      return;
    }
    if(status){
      card.classList.add('is-unavailable');
      card.classList.toggle('is-coming-soon',status==='coming_soon');
      if(actions)actions.style.display='none';
      if(!badge){badge=document.createElement('div');badge.className='unavailable-badge';card.appendChild(badge);}
      badge.style.display='';
      badge.classList.toggle('coming-soon-badge',status==='coming_soon');
    }
    if(badge&&statusText)text(badge,statusText);
  }

  function applyHomepagePrices(overrides){
    const weekday=byPath(overrides,'prices.starzik.weekday')||{};
    const weekend=byPath(overrides,'prices.starzik.weekend')||{};
    const surcharge=Number(byPath(overrides,'prices.starzik.lateNightSurcharge'))||0;
    const ids=['2','3','4','5'];
    const tiers={
      'weekday-standard':{prices:weekday,extra:0},
      'weekday-late':{prices:weekday,extra:surcharge},
      'weekend-standard':{prices:weekend,extra:0},
      'weekend-late':{prices:weekend,extra:surcharge}
    };
    Object.entries(tiers).forEach(([tier,cfg])=>{
      const block=document.querySelector(`#tab-starzik [data-price-tier="${tier}"]`);if(!block)return;
      [...block.querySelectorAll('.price-row')].forEach((row,index)=>{
        const id=ids[index];if(!Object.prototype.hasOwnProperty.call(cfg.prices,id))return;
        text(row.querySelector('.price-amount-main')||row.querySelector('.price-amount'),money((Number(cfg.prices[id])||0)+cfg.extra));
      });
    });
    const tesla=byPath(overrides,'prices.tesla')||{};
    const teslaRows=[...document.querySelectorAll('#tab-tesla .price-block:first-child .price-row')];
    ['1','2'].forEach((id,index)=>{if(Object.prototype.hasOwnProperty.call(tesla,id))text(teslaRows[index]?.querySelector('.price-amount'),money(tesla[id]));});
  }

  function applyPricePage(overrides){
    const ids=['2','3','4','5'];
    const weekday=byPath(overrides,'prices.starzik.weekday')||{};
    const weekend=byPath(overrides,'prices.starzik.weekend')||{};
    const surcharge=Number(byPath(overrides,'prices.starzik.lateNightSurcharge'))||0;
    const tiers={
      'weekday-standard':{prices:weekday,extra:0},
      'weekday-late':{prices:weekday,extra:surcharge},
      'weekend-standard':{prices:weekend,extra:0},
      'weekend-late':{prices:weekend,extra:surcharge}
    };
    let found=false;
    Object.entries(tiers).forEach(([tier,cfg])=>{
      const card=document.querySelector(`#starzik-prices [data-price-tier="${tier}"]`);if(!card)return;
      found=true;
      [...card.querySelectorAll('tbody tr')].forEach((row,index)=>{
        const id=ids[index];if(!Object.prototype.hasOwnProperty.call(cfg.prices,id))return;
        text(row.querySelector('td strong'),money((Number(cfg.prices[id])||0)+cfg.extra));
      });
    });
    if(!found)return;
    if(Object.prototype.hasOwnProperty.call(weekday,'2')){
      const fact=[...document.querySelectorAll('.facts .fact')].find(x=>/za grupę/i.test(x.textContent||''));
      if(fact)text(fact.querySelector('strong'),`od ${money(weekday['2'])}`);
    }
  }

  const HOME_PROMO_IDS=['names','tme','workers','senior','theszpil'];
  const PRICE_PROMO_IDS=['names','tme','workers','senior','theszpil'];
  function applyPromotionCards(cards,ids,overrides){
    ids.forEach((id,index)=>{
      const cfg=byPath(overrides,`promotions.items.${id}`);if(!cfg)return;
      const card=cards[index];if(!card)return;
      if(Object.prototype.hasOwnProperty.call(cfg,'title'))text(card.querySelector('.rabat-name,h3'),cfg.title);
      if(Object.prototype.hasOwnProperty.call(cfg,'text'))text(card.querySelector('.rabat-desc,p'),cfg.text);
    });
  }

  function applyPromotions(overrides){
    if(hasPath(overrides,'promotions.intro')){
      const intro=document.querySelector('#cennik .rabaty-grid')?.previousElementSibling;
      if(intro?.classList.contains('section-intro'))text(intro,byPath(overrides,'promotions.intro'));
      const priceIntro=document.querySelector('#promocje .note');
      if(priceIntro)text(priceIntro,byPath(overrides,'promotions.intro'));
    }
    const homeCards=[...document.querySelectorAll('#cennik .rabaty-grid .rabat-card')];
    if(homeCards.length)applyPromotionCards(homeCards,HOME_PROMO_IDS,overrides);
    const priceCards=[...document.querySelectorAll('#promocje .cards .card')];
    if(priceCards.length)applyPromotionCards(priceCards,PRICE_PROMO_IDS,overrides);
  }

  function applyFaq(overrides){
    const faq=byPath(overrides,'faq');if(!faq||typeof faq!=='object')return;
    Object.entries(faq).forEach(([id,cfg])=>{
      if(!cfg||typeof cfg!=='object')return;
      const item=document.querySelector(`#faq-a-${CSS.escape(String(id))}`)?.closest('.faq-item');
      if(!item)return;
      if(Object.prototype.hasOwnProperty.call(cfg,'question'))text(item.querySelector('.faq-q span:first-child'),cfg.question);
      if(Object.prototype.hasOwnProperty.call(cfg,'answer'))text(item.querySelector('.faq-a'),cfg.answer);
    });
  }

  function applyContent(payload){
    const overrides=payload&&payload.overrides&&typeof payload.overrides==='object'?payload.overrides:{};
    setText('#home .hero-tagline',overrides,'home.heroTagline');
    setText('#home .hero-sub',overrides,'home.heroIntro');
    setText('.opening-eyebrow',overrides,'home.noticeEyebrow');
    setText('#opening-title',overrides,'home.noticeTitle');
    setText('#opening-copy',overrides,'home.noticeText');
    setText('#opening-book',overrides,'home.noticeButton');
    ['starzik','frelka','tesla'].forEach(id=>applyRoom(overrides,id));
    applyHomepagePrices(overrides);
    applyPricePage(overrides);
    applyPromotions(overrides);
    applyFaq(overrides);
  }

  fetch(CONTENT_URL,{cache:'no-store',headers:{Accept:'application/json'}})
    .then(response=>response.ok?response.json():Promise.reject(new Error(`site-content HTTP ${response.status}`)))
    .then(applyContent)
    .catch(error=>console.warn('Familock site content',error));
})();
