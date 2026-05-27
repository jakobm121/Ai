import os, json, math, itertools
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

TZ='Europe/Ljubljana'
DATA_DIR='data'
OUT='tennis_optimizer'
RESULTS=f'{DATA_DIR}/tennis_results.json'
REPORT=f'{OUT}/tennis_optimizer_report.md'
BEST=f'{OUT}/tennis_best_rules.json'
TABLE=f'{OUT}/tennis_optimizer_table.json'
PICKS=f'{OUT}/tennis_optimizer_picks.json'
DEBUG=f'{OUT}/tennis_optimizer_debug.json'
SUMMARY=f'{OUT}/tennis_optimizer_summary.json'
TACTIC=f'{OUT}/tennis_optimizer_tactic.json'

MIN_PICKS=int(os.getenv('MIN_PICKS','100'))
TOP_N=int(os.getenv('TOP_N','75'))
BEAM_WIDTH=int(os.getenv('BEAM_WIDTH','350'))
MAX_DEPTH=int(os.getenv('MAX_RULE_DEPTH','5'))
STAKE=1.0

# Beam search pomeni: dovolj globoko križa filtre, ampak ne eksplodira v 20+ minut.
NUM_FILTERS={
 'confidence_min':('confidence','>=',[50,55,60,65,70,75,80,85,88,90]),
 'confidence_max':('confidence','<=',[75,80,85,88,90,93,96]),
 'quality_min':('quality','>=',[50,55,60,65,70,72,75,80,85,88]),
 'quality_max':('quality','<=',[70,75,80,85,88,90,93]),
 'edge_min':('edge','>=',[0,0.02,0.04,0.06,0.08,0.10,0.12,0.15]),
 'edge_max':('edge','<=',[0.04,0.06,0.08,0.10,0.12,0.15,0.20]),
 'odds_min':('odds','>=',[1.30,1.45,1.60,1.70,1.75,1.85,1.90,2.00,2.05,2.15]),
 'odds_max':('odds','<=',[1.70,1.85,1.90,2.00,2.10,2.25,2.40,2.60,3.00]),
 'market_gap_min':('market_gap','>=',[0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50]),
 'market_gap_max':('market_gap','<=',[0.20,0.25,0.35,0.50,0.70,0.90]),
 'strength_gap_min':('strength_gap','>=',[3,5,8,10,15,20,30,40,50]),
 'strength_gap_max':('strength_gap','<=',[5,10,15,20,30,40,60,100]),
 'h2h_max':('h2h','<=',[0,1,2,3,5]),
 'bookmakers_min':('bookmakers','>=',[2,3,4,5,6,7,8,9]),
 'bookmakers_max':('bookmakers','<=',[3,4,5,6,7,8,10]),
 'rank_min':('rank','>=',[5,10,20,30,50]),
 'rank_max':('rank','<=',[5,10,20,30,50,100]),
}
CAT_FILTERS={
 'side':['home','away'],
 'gender':['men','women'],
 'tour_level':['atp','wta','challenger','itf'],
 'qualification':[True,False],
}
LABEL={
 'confidence_min':'confidence ≥','confidence_max':'confidence ≤','quality_min':'quality ≥','quality_max':'quality ≤',
 'edge_min':'edge ≥','edge_max':'edge ≤','odds_min':'odds ≥','odds_max':'odds ≤',
 'market_gap_min':'market gap ≥','market_gap_max':'market gap ≤','strength_gap_min':'strength gap ≥','strength_gap_max':'strength gap ≤',
 'h2h_max':'h2h ≤','bookmakers_min':'bookmakers ≥','bookmakers_max':'bookmakers ≤',
 'rank_min':'rank ≥','rank_max':'rank ≤','side':'side =','gender':'gender =','tour_level':'tour =','qualification':'qualification =',
}
BUCKETS={
 'confidence':[('<75',None,74.999),('75-79.9',75,79.999),('80-84.9',80,84.999),('85-87.9',85,87.999),('88-89.9',88,89.999),('90+',90,None)],
 'quality':[('<72',None,71.999),('72-74.9',72,74.999),('75-79.9',75,79.999),('80-84.9',80,84.999),('85+',85,None)],
 'edge':[('<0.04',None,0.0399),('0.04-0.059',0.04,0.0599),('0.06-0.079',0.06,0.0799),('0.08-0.099',0.08,0.0999),('0.10-0.119',0.10,0.1199),('0.12+',0.12,None)],
 'odds':[('<1.60',None,1.599),('1.60-1.749',1.60,1.749),('1.75-1.899',1.75,1.899),('1.90-2.049',1.90,2.049),('2.05-2.249',2.05,2.249),('2.25+',2.25,None)],
 'market_gap':[('<0.15',None,0.149),('0.15-0.249',0.15,0.249),('0.25-0.349',0.25,0.349),('0.35-0.499',0.35,0.499),('0.50+',0.50,None)],
 'strength_gap':[('<5',None,4.999),('5-9.9',5,9.999),('10-19.9',10,19.999),('20-29.9',20,29.999),('30-49.9',30,49.999),('50+',50,None)],
 'bookmakers':[('<4',None,3.999),('4-5',4,5.999),('6-7',6,7.999),('8+',8,None)],
 'rank':[('1-10',1,10),('11-20',11,20),('21-50',21,50),('51+',51,None)],
}

def ensure(): os.makedirs(OUT,exist_ok=True)
def now(): return datetime.now(ZoneInfo(TZ)).isoformat()
def load(path,default):
    try:
        with open(path,'r',encoding='utf-8') as f: x=json.load(f)
        return x if isinstance(x,type(default)) else default
    except Exception: return default
def save(path,x):
    ensure();
    with open(path,'w',encoding='utf-8') as f: json.dump(x,f,indent=2,ensure_ascii=False); f.write('\n')
def text(path,s):
    ensure(); open(path,'w',encoding='utf-8').write(s)
def fl(x,d=None):
    try:
        if x is None or x=='': return d
        v=float(x)
        return d if math.isnan(v) or math.isinf(v) else v
    except Exception: return d
def it(x,d=None):
    try:
        if x is None or x=='': return d
        return int(float(x))
    except Exception: return d
def nested(d,path,default=None):
    c=d
    for p in path.split('.'):
        if not isinstance(c,dict) or p not in c: return default
        c=c[p]
    return c
def res(x):
    r=str(x or '').lower().strip()
    if r in ('win','won','w'): return 'win'
    if r in ('loss','lost','lose','l'): return 'loss'
    if r in ('push','void','cancelled','canceled'): return 'push'
    if r=='pending': return 'pending'
    return r
def side(p):
    raw=str(p.get('side') or p.get('pick') or p.get('selection') or '').lower().strip()
    if raw in ('home','first','1','first_player','player1'): return 'home'
    if raw in ('away','second','2','second_player','player2'): return 'away'
    bet=str(p.get('bet') or '').lower(); a=str(p.get('first_player_name') or '').lower(); b=str(p.get('second_player_name') or '').lower()
    if a and a in bet: return 'home'
    if b and b in bet: return 'away'
    return raw or None
def profit(p):
    r=res(p.get('result')); o=fl(p.get('odds'))
    if r=='win': return round(STAKE*((o or 1)-1),4)
    if r=='loss': return -STAKE
    return 0.0
def feats(p):
    mi=p.get('market_info') if isinstance(p.get('market_info'),dict) else {}
    fs=fl(p.get('first_strength_score')); ss=fl(p.get('second_strength_score')); sg=fl(p.get('strength_gap'))
    if sg is None and fs is not None and ss is not None: sg=abs(fs-ss)
    mg=fl(mi.get('market_gap'))
    if mg is None:
        hi=fl(mi.get('home_implied')); ai=fl(mi.get('away_implied'))
        if hi is not None and ai is not None: mg=abs(hi-ai)
    return {
      'confidence':fl(p.get('confidence')),'quality':fl(p.get('quality_score')),'edge':fl(p.get('edge')),
      'odds':fl(p.get('odds')),'bookmakers':it(p.get('bookmakers_used')),'rank':it(p.get('rank')),
      'market_gap':mg,'strength_gap':abs(sg) if sg is not None else None,'h2h':it(p.get('h2h_matches')),
      'side':side(p),'gender':str(p.get('gender') or '').lower() or None,'tour_level':str(p.get('tour_level') or '').lower() or None,
      'qualification':p.get('qualification') if isinstance(p.get('qualification'),bool) else None,
    }
def enrich(p,i):
    q=dict(p); q['_idx']=i; q['_result_norm']=res(p.get('result')); q['_profit_flat']=profit(p); q['_features']=feats(p); return q
def skey(p): return (str(p.get('date') or ''),str(p.get('time') or ''),str(p.get('created_at') or ''),str(p.get('pick_id') or ''))
def dd(profs):
    b=peak=mdd=0.0
    for x in profs:
        b+=x; peak=max(peak,b); mdd=min(mdd,b-peak)
    return round(mdd,4)
def streak(rs,t):
    best=cur=0
    for r in rs:
        if r==t: cur+=1; best=max(best,cur)
        else: cur=0
    return best
def stats(ps):
    ps=[p for p in ps if p.get('_result_norm') in ('win','loss','push')]
    w=sum(1 for p in ps if p['_result_norm']=='win'); l=sum(1 for p in ps if p['_result_norm']=='loss'); pu=sum(1 for p in ps if p['_result_norm']=='push')
    profs=[p.get('_profit_flat',0) for p in ps]; pr=round(sum(profs),4); stake=len(ps)*STAKE
    odds=[fl(p.get('odds')) for p in ps if fl(p.get('odds')) is not None]
    rs=[p['_result_norm'] for p in ps]
    return {'picks':len(ps),'wins':w,'losses':l,'pushes':pu,'winrate':round(w/max(1,w+l)*100,2),'profit':pr,'roi':round(pr/max(1,stake)*100,2),'avg_odds':round(sum(odds)/len(odds),4) if odds else 0,'max_drawdown':dd(profs),'longest_win_streak':streak(rs,'win'),'longest_loss_streak':streak(rs,'loss')}
def split(ps):
    ps=sorted(ps,key=skey)
    if len(ps)<4: return ps,[]
    c=max(1,min(int(len(ps)*0.75),len(ps)-1)); return ps[:c],ps[c:]
def score(st,te=None):
    if st['picks']<MIN_PICKS: return -999999
    s=st['profit']+st['roi']*.35+st['winrate']*.15+st['avg_odds']*.10+math.log(max(1,st['picks']))*.08-abs(st['max_drawdown'])*.60
    if te and te['picks']>=max(10,int(MIN_PICKS*.2)): s+=te['profit']*.55+te['roi']*.18
    return round(s,6)
def clean(r): return {k:r[k] for k in sorted(r) if r[k] is not None}
def rkey(r): return json.dumps(clean(r),sort_keys=True,ensure_ascii=False)
def valid(r):
    for lo,hi in [('odds_min','odds_max'),('confidence_min','confidence_max'),('quality_min','quality_max'),('edge_min','edge_max'),('market_gap_min','market_gap_max'),('strength_gap_min','strength_gap_max'),('bookmakers_min','bookmakers_max'),('rank_min','rank_max')]:
        if r.get(lo) is not None and r.get(hi) is not None and r[lo]>r[hi]: return False
    return True
def merge(a,b):
    r=dict(a)
    for k,v in b.items():
        if k in r and r[k]!=v: return None
        r[k]=v
    return clean(r) if valid(r) else None
def passes(p,r):
    f=p.get('_features',{})
    for k,(fk,op,_) in NUM_FILTERS.items():
        if k not in r: continue
        v=f.get(fk)
        if v is None: return False
        if op=='>=' and v<r[k]: return False
        if op=='<=' and v>r[k]: return False
    for k in CAT_FILTERS:
        if k in r and f.get(k)!=r[k]: return False
    return True
def fmt(r):
    r=clean(r)
    return 'No filters' if not r else '; '.join(f"{LABEL.get(k,k)} {v}" for k,v in r.items())
def atoms():
    a=[]
    for k,(_,_,vals) in NUM_FILTERS.items():
        a += [{k:v} for v in vals]
    for k,vals in CAT_FILTERS.items():
        a += [{k:v} for v in vals]
    seen=set(); out=[]
    for x in a:
        kk=rkey(x)
        if kk not in seen: seen.add(kk); out.append(x)
    return out
def eval_rule(ps,r):
    sel=[p for p in ps if passes(p,r)]
    st=stats(sel); tr,te=split(sel); ts=stats(tr); es=stats(te)
    return {'score':score(st,es),'rules':clean(r),'stats':st,'train_75_stats':ts,'test_25_stats':es},sel
def beam(ps):
    at=atoms(); evaluated={}; beam=[{}]
    row,_=eval_rule(ps,{}); evaluated[rkey({})]=row
    for depth in range(1,MAX_DEPTH+1):
        cand=[]
        for base in beam:
            for a in at:
                r=merge(base,a)
                if r is None: continue
                k=rkey(r)
                if k in evaluated: continue
                row,_=eval_rule(ps,r); evaluated[k]=row
                if row['stats']['picks']>=max(20,int(MIN_PICKS*.25)): cand.append(row)
        cand.sort(key=lambda x:(x['score'],x['stats']['profit'],x['test_25_stats']['profit'],x['stats']['roi'],x['stats']['picks']),reverse=True)
        beam=[x['rules'] for x in cand[:BEAM_WIDTH]]
        if not beam: break
    rows=[x for x in evaluated.values() if x['stats']['picks']>=MIN_PICKS and x['score']>-999999]
    rows.sort(key=lambda x:(x['score'],x['stats']['profit'],x['test_25_stats']['profit'],x['stats']['roi'],x['stats']['picks']),reverse=True)
    return rows,{'atomic_filters':len(at),'rules_evaluated_total':len(evaluated),'valid_rules_over_min_sample':len(rows),'beam_width':BEAM_WIDTH,'max_rule_depth':MAX_DEPTH}
def group_break(ps,field):
    g=defaultdict(list)
    for p in ps:
        v=p.get('_features',{}).get(field.split('.',1)[1]) if field.startswith('_features.') else nested(p,field)
        g[str(v if v not in (None,'') else 'unknown')].append(p)
    rows=[{'group':k,**stats(v)} for k,v in g.items()]
    rows.sort(key=lambda x:(x['profit'],x['roi'],x['picks']),reverse=True); return rows
def bucket_label(v,b):
    if v is None: return 'unknown'
    for lab,lo,hi in b:
        if lo is not None and v<lo: continue
        if hi is not None and v>hi: continue
        return lab
    return 'other'
def bucket_break(ps,feat):
    g=defaultdict(list)
    for p in ps: g[bucket_label(p.get('_features',{}).get(feat),BUCKETS[feat])].append(p)
    rows=[{'bucket':k,**stats(v)} for k,v in g.items()]
    rows.sort(key=lambda x:(x['profit'],x['roi'],x['picks']),reverse=True); return rows
def ranges(ps,feat):
    vals=sorted([p.get('_features',{}).get(feat) for p in ps if isinstance(p.get('_features',{}).get(feat),(int,float))])
    if not vals: return None
    n=len(vals); q=lambda x: round(vals[int(round((n-1)*x))],4)
    return {'min':round(vals[0],4),'p25':q(.25),'median':q(.5),'p75':q(.75),'max':round(vals[-1],4),'avg':round(sum(vals)/n,4)}
def bucket_rule(feat,lab):
    m={
     'confidence':{'<75':{'confidence_max':74.999},'75-79.9':{'confidence_min':75,'confidence_max':79.999},'80-84.9':{'confidence_min':80,'confidence_max':84.999},'85-87.9':{'confidence_min':85,'confidence_max':87.999},'88-89.9':{'confidence_min':88,'confidence_max':89.999},'90+':{'confidence_min':90}},
     'quality':{'<72':{'quality_max':71.999},'72-74.9':{'quality_min':72,'quality_max':74.999},'75-79.9':{'quality_min':75,'quality_max':79.999},'80-84.9':{'quality_min':80,'quality_max':84.999},'85+':{'quality_min':85}},
     'edge':{'<0.04':{'edge_max':0.0399},'0.04-0.059':{'edge_min':0.04,'edge_max':0.0599},'0.06-0.079':{'edge_min':0.06,'edge_max':0.0799},'0.08-0.099':{'edge_min':0.08,'edge_max':0.0999},'0.10-0.119':{'edge_min':0.10,'edge_max':0.1199},'0.12+':{'edge_min':0.12}},
     'odds':{'<1.60':{'odds_max':1.599},'1.60-1.749':{'odds_min':1.60,'odds_max':1.749},'1.75-1.899':{'odds_min':1.75,'odds_max':1.899},'1.90-2.049':{'odds_min':1.90,'odds_max':2.049},'2.05-2.249':{'odds_min':2.05,'odds_max':2.249},'2.25+':{'odds_min':2.25}},
     'market_gap':{'<0.15':{'market_gap_max':0.149},'0.15-0.249':{'market_gap_min':0.15,'market_gap_max':0.249},'0.25-0.349':{'market_gap_min':0.25,'market_gap_max':0.349},'0.35-0.499':{'market_gap_min':0.35,'market_gap_max':0.499},'0.50+':{'market_gap_min':0.50}},
     'strength_gap':{'<5':{'strength_gap_max':4.999},'5-9.9':{'strength_gap_min':5,'strength_gap_max':9.999},'10-19.9':{'strength_gap_min':10,'strength_gap_max':19.999},'20-29.9':{'strength_gap_min':20,'strength_gap_max':29.999},'30-49.9':{'strength_gap_min':30,'strength_gap_max':49.999},'50+':{'strength_gap_min':50}},
     'bookmakers':{'<4':{'bookmakers_max':3.999},'4-5':{'bookmakers_min':4,'bookmakers_max':5.999},'6-7':{'bookmakers_min':6,'bookmakers_max':7.999},'8+':{'bookmakers_min':8}},
     'rank':{'1-10':{'rank_min':1,'rank_max':10},'11-20':{'rank_min':11,'rank_max':20},'21-50':{'rank_min':21,'rank_max':50},'51+':{'rank_min':51}},
    }
    return m.get(feat,{}).get(lab)
def addon_combos(base):
    minp=max(20,int(len(base)*.18)); a=[]
    for feat in BUCKETS:
        for row in bucket_break(base,feat):
            if row['picks']>=minp:
                rr=bucket_rule(feat,row['bucket'])
                if rr: a.append({'label':f"{feat}={row['bucket']}",'rule':rr})
    for feat in CAT_FILTERS:
        g=defaultdict(list)
        for p in base:
            v=p.get('_features',{}).get(feat)
            if v is not None: g[v].append(p)
        for v,items in g.items():
            if len(items)>=minp: a.append({'label':f'{feat}={v}','rule':{feat:v}})
    out=[]; seen=set()
    for d in (1,2,3):
        for combo in itertools.combinations(a,d):
            r={}; labels=[]; ok=True
            for atom in combo:
                r=merge(r,atom['rule'])
                if r is None: ok=False; break
                labels.append(atom['label'])
            if not ok or rkey(r) in seen: continue
            seen.add(rkey(r)); sel=[p for p in base if passes(p,r)]
            if len(sel)<minp: continue
            st=stats(sel); tr,te=split(sel); ts=stats(tr); es=stats(te)
            sc=round(st['profit']+st['roi']*.25+st['winrate']*.10-abs(st['max_drawdown'])*.40+math.log(max(1,st['picks']))*.15+es['profit']*.35,6)
            out.append({'score':sc,'labels':labels,'rules':r,'stats':st,'train_75_stats':ts,'test_25_stats':es})
    out.sort(key=lambda x:(x['score'],x['stats']['profit'],x['test_25_stats']['profit'],x['stats']['roi'],x['stats']['picks']),reverse=True)
    return out
def negative(base):
    out=[]
    for name,field in {'side':'_features.side','gender':'_features.gender','tour':'_features.tour_level','qualification':'_features.qualification','bookmaker':'best_bookmaker','tournament':'tournament'}.items():
        for r in group_break(base,field):
            if r['picks']>=max(8,int(len(base)*.06)) and r['profit']<0:
                r=dict(r); r['reason']=name; out.append(r)
    for feat in BUCKETS:
        for r in bucket_break(base,feat):
            if r['picks']>=max(8,int(len(base)*.06)) and r['profit']<0:
                r=dict(r); r['reason']=feat; r['group']=r['bucket']; out.append(r)
    out.sort(key=lambda x:(x['profit'],x['roi'])); return out
def tactic(best,addons,negs):
    t={'base_rules':best['rules'] if best else {},'base_stats':best['stats'] if best else {},'stake':{'forward_test':'0.5u flat for next 50 live picks','confirmed':'1u flat only after forward confirmation','avoid':'no martingale'},'priority_a':[],'priority_b':[],'avoid':[]}
    if not best: return t
    for r in addons:
        s=r['stats']; te=r['test_25_stats']
        item={'rules':r['rules'],'labels':r['labels'],'stats':s,'test_25_stats':te}
        if s['profit']>0 and s['roi']>best['stats']['roi'] and te['profit']>=0 and len(t['priority_a'])<5: t['priority_a'].append(item)
        elif s['profit']>0 and s['roi']>0 and len(t['priority_b'])<5: t['priority_b'].append(item)
    for r in negs[:10]:
        t['avoid'].append({'reason':r.get('reason'),'group':r.get('group'),'stats':{k:r[k] for k in ('picks','winrate','profit','roi','avg_odds','max_drawdown') if k in r}})
    return t
def mdrow(name,st): return f"| {name} | {st['picks']} | {st['wins']} | {st['losses']} | {st['pushes']} | {st['winrate']}% | {st['profit']}u | {st['roi']}% | {st['avg_odds']} | {st['max_drawdown']}u |"
def report(generated,src,settled,base,best,top,bp,breaks,buckets,rng,adds,negs,tac,dbg):
    L=['# Tennis Home/Away Optimizer Report','',f'Generated at: **{generated}**','', '## Executive summary','',f'- Source picks loaded: **{src}**',f'- Settled picks used: **{settled}**',f'- Minimum sample: **{MIN_PICKS}**',f'- Rules evaluated: **{dbg.get("rules_evaluated_total",0)}**',f'- Valid strategies: **{dbg.get("valid_rules_over_min_sample",0)}**','', '## Whole database baseline','','| Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|',mdrow('All',base).replace('| All |','|')]
    if not best:
        L+=['','No valid strategy found.']; return '\n'.join(L)+'\n'
    L+=['','## Best strategy found','',f'**Score:** {best["score"]}','',f'**Rules:** {fmt(best["rules"])}','', '| Split | Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|',mdrow('Full',best['stats']),mdrow('Train 75%',best['train_75_stats']),mdrow('Test 25%',best['test_25_stats']),'','## Recommended live tactic','','### Base filter','','```json',json.dumps(best['rules'],indent=2,ensure_ascii=False),'```','','### Stake','','- Forward test: **0.5u flat** until 50 new live picks.','- Confirmed mode: **1u flat** only after forward confirmation.','- No martingale.','','### A-pick priority','','| Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |','|---|---:|---:|---:|---:|---:|---:|']
    if tac['priority_a']:
        for x in tac['priority_a']:
            s=x['stats']; te=x['test_25_stats']; L.append(f"| {fmt(x['rules'])} | {s['picks']} | {s['winrate']}% | {s['profit']}u | {s['roi']}% | {te['profit']}u | {te['roi']}% |")
    else: L.append('| No stable A add-on | - | - | - | - | - | - |')
    L+=['','### B-pick watchlist','','| Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |','|---|---:|---:|---:|---:|---:|---:|']
    if tac['priority_b']:
        for x in tac['priority_b']:
            s=x['stats']; te=x['test_25_stats']; L.append(f"| {fmt(x['rules'])} | {s['picks']} | {s['winrate']}% | {s['profit']}u | {s['roi']}% | {te['profit']}u | {te['roi']}% |")
    else: L.append('| No B watchlist | - | - | - | - | - | - |')
    L+=['','### Avoid / weak segments','','| Reason | Group | Picks | Winrate | Profit | ROI |','|---|---|---:|---:|---:|---:|']
    if tac['avoid']:
        for x in tac['avoid']:
            s=x['stats']; L.append(f"| {x.get('reason')} | {x.get('group')} | {s.get('picks')} | {s.get('winrate')}% | {s.get('profit')}u | {s.get('roi')}% |")
    else: L.append('| None | None | - | - | - | - |')
    L+=['','## Tactical add-on combinations inside best base','','| Rank | Score | Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |','|---:|---:|---|---:|---:|---:|---:|---:|---:|']
    for i,r in enumerate(adds[:30],1):
        s=r['stats']; te=r['test_25_stats']; L.append(f"| {i} | {r['score']} | {fmt(r['rules'])} | {s['picks']} | {s['winrate']}% | {s['profit']}u | {s['roi']}% | {te['profit']}u | {te['roi']}% |")
    L+=['','## Top global strategies','','| Rank | Score | Picks | Winrate | Profit | ROI | Test profit | Test ROI | Max DD | Rules |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for i,r in enumerate(top[:25],1):
        s=r['stats']; te=r['test_25_stats']; L.append(f"| {i} | {r['score']} | {s['picks']} | {s['winrate']}% | {s['profit']}u | {s['roi']}% | {te['profit']}u | {te['roi']}% | {s['max_drawdown']}u | {fmt(r['rules'])} |")
    L+=['','## Feature ranges inside best strategy','','| Feature | Min | P25 | Median | P75 | Max | Avg |','|---|---:|---:|---:|---:|---:|---:|']
    for f,d in rng.items():
        if d: L.append(f"| {f} | {d['min']} | {d['p25']} | {d['median']} | {d['p75']} | {d['max']} | {d['avg']} |")
    L+=['','## Bucket analysis inside best strategy']
    for f,rows in buckets.items():
        L+=['',f'### {f}','','| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |','|---|---:|---:|---:|---:|---:|---:|']
        for r in rows: L.append(f"| {r['bucket']} | {r['picks']} | {r['winrate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} | {r['max_drawdown']}u |")
    L+=['','## Categorical breakdown inside best strategy']
    for title,rows in breaks.items():
        L+=['',f'### {title}','','| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |','|---|---:|---:|---:|---:|---:|---:|']
        for r in rows[:20]: L.append(f"| {r['group']} | {r['picks']} | {r['winrate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} | {r['max_drawdown']}u |")
    L+=['','## Files generated','',f'- `{REPORT}`',f'- `{BEST}`',f'- `{TABLE}`',f'- `{PICKS}`',f'- `{TACTIC}`',f'- `{DEBUG}`',f'- `{SUMMARY}`','']
    return '\n'.join(L)+'\n'
def pub(p):
    x=dict(p); x.pop('_features',None); return x

def main():
    ensure(); raw=load(RESULTS,[])
    if not isinstance(raw,list): raw=[]
    enriched=[enrich(p,i) for i,p in enumerate(raw) if isinstance(p,dict)]
    settled=[p for p in enriched if p.get('_result_norm') in ('win','loss','push')]
    base=stats(settled)
    top,dbg=beam(settled); top=top[:TOP_N]; best=top[0] if top else None
    bp=[]; breaks={}; buckets={}; rng={}; adds=[]; negs=[]; tac=tactic(None,[],[])
    if best:
        bp=[p for p in settled if passes(p,best['rules'])]
        breaks={'By side':group_break(bp,'_features.side'),'By gender':group_break(bp,'_features.gender'),'By tour level':group_break(bp,'_features.tour_level'),'By bookmaker':group_break(bp,'best_bookmaker'),'By tournament':group_break(bp,'tournament')}
        for f in BUCKETS:
            buckets[f]=bucket_break(bp,f); rng[f]=ranges(bp,f)
        adds=addon_combos(bp); negs=negative(bp); tac=tactic(best,adds,negs)
    gen=now()
    save(SUMMARY,{'generated_at':gen,'source_file':RESULTS,'source_count':len(raw),'settled_count':len(settled),'min_picks':MIN_PICKS,'baseline':base,'best':best,'output_dir':OUT})
    save(BEST,best['rules'] if best else {})
    save(TABLE,top)
    save(PICKS,[pub(p) for p in bp])
    save(TACTIC,tac)
    save(DEBUG,{'generated_at':gen,'source_file':RESULTS,'source_count':len(raw),'settled_count':len(settled),'missing_or_pending_count':len(enriched)-len(settled),'min_picks':MIN_PICKS,'top_n':TOP_N,'num_filters':NUM_FILTERS,'cat_filters':CAT_FILTERS,**dbg})
    text(REPORT,report(gen,len(raw),len(settled),base,best,top,bp,breaks,buckets,rng,adds,negs,tac,dbg))
    print('\nTENNIS OPTIMIZER DONE')
    print(f'source picks: {len(raw)}')
    print(f'settled picks: {len(settled)}')
    print(f'rules evaluated total: {dbg.get("rules_evaluated_total")}')
    print(f'valid rules over min sample: {dbg.get("valid_rules_over_min_sample")}')
    if best:
        print('\nBEST RULES:'); print(json.dumps(best['rules'],indent=2,ensure_ascii=False))
        print('\nFULL:'); print(best['stats'])
        print('TRAIN 75%:'); print(best['train_75_stats'])
        print('TEST 25%:'); print(best['test_25_stats'])
    else:
        print('No valid strategy found. Try lowering MIN_PICKS.')
    print(f'\nReport: {REPORT}')

if __name__=='__main__': main()
