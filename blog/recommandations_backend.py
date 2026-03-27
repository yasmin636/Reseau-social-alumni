{% extends ‘base.html’ %}
{% load static %}

{% block title %}Recommandations – Réseau Alumni{% endblock %}

{% block extra_css %}

<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  :root {
    --bg-deep:    #0d0d14;
    --bg-card:    #13131f;
    --bg-hover:   #1a1a2e;
    --border:     rgba(255,255,255,0.06);
    --pink:       #e040a0;
    --cyan:       #00e5ff;
    --purple:     #a855f7;
    --text-main:  #f0f0ff;
    --text-muted: #7a7a9a;
    --radius:     16px;
  }

  .reco-header {
    padding: 2.5rem 2rem 1.5rem;
    border-bottom: 1px solid var(--border);
  }

  .reco-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(120deg, var(--pink), var(--purple), var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline-block;
  }

  .reco-header p {
    color: var(--text-muted);
    margin-top: 0.4rem;
    font-size: 0.92rem;
  }

  .filter-tabs {
    display: flex;
    gap: 0.6rem;
    padding: 1.2rem 2rem;
    flex-wrap: wrap;
  }

  .tab {
    padding: 0.4rem 1rem;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'DM Sans', sans-serif;
  }

  .tab:hover, .tab.active {
    background: linear-gradient(135deg, var(--pink), var(--purple));
    border-color: transparent;
    color: #fff;
  }

  .reco-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.2rem;
    padding: 0.5rem 2rem 3rem;
  }

  .alumni-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
    animation: fadeUp 0.4s ease both;
  }

  .alumni-card:hover {
    transform: translateY(-4px);
    border-color: rgba(168,85,247,0.4);
    box-shadow: 0 12px 40px rgba(168,85,247,0.12);
  }

  .card-banner {
    height: 70px;
    background: linear-gradient(135deg,
      rgba(224,64,160,0.6) 0%,
      rgba(168,85,247,0.6) 50%,
      rgba(0,229,255,0.4) 100%);
    position: relative;
  }

  .shared-tag {
    position: absolute;
    top: 0.55rem;
    right: 0.55rem;
    font-size: 0.7rem;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    background: rgba(0,0,0,0.55);
    border: 1px solid rgba(255,255,255,0.15);
    color: var(--cyan);
    backdrop-filter: blur(4px);
    white-space: nowrap;
  }

  .card-avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 3px solid var(--bg-card);
    object-fit: cover;
    position: absolute;
    bottom: -32px;
    left: 1.2rem;
    background: var(--bg-hover);
  }

  .card-avatar-placeholder {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 3px solid var(--bg-card);
    position: absolute;
    bottom: -32px;
    left: 1.2rem;
    background: linear-gradient(135deg, var(--purple), var(--pink));
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.2rem;
    color: #fff;
  }

  .card-body {
    padding: 2.5rem 1.2rem 1.2rem;
  }

  .card-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: var(--text-main);
    margin-bottom: 0.15rem;
  }

  .card-role {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
    line-height: 1.4;
  }

  .card-reason {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    color: var(--purple);
    background: rgba(168,85,247,0.1);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 8px;
    padding: 0.4rem 0.7rem;
    margin-bottom: 1rem;
  }

  .skills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-bottom: 1rem;
  }

  .skill-badge {
    font-size: 0.68rem;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    color: var(--cyan);
  }

  .card-actions {
    display: flex;
    gap: 0.6rem;
  }

  .btn-follow {
    flex: 1;
    padding: 0.5rem 0;
    border-radius: 10px;
    border: none;
    background: linear-gradient(135deg, var(--pink), var(--purple));
    color: #fff;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.2s;
    font-family: 'DM Sans', sans-serif;
  }

  .btn-follow:hover { opacity: 0.85; }

  .btn-follow.following {
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--border);
    color: var(--text-muted);
  }

  .btn-profil {
    padding: 0.5rem 0.9rem;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'DM Sans', sans-serif;
    text-decoration: none;
    display: flex;
    align-items: center;
  }

  .btn-profil:hover {
    border-color: var(--purple);
    color: var(--text-main);
  }

  .empty-state {
    grid-column: 1/-1;
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .alumni-card:nth-child(1) { animation-delay: 0.05s; }
  .alumni-card:nth-child(2) { animation-delay: 0.10s; }
  .alumni-card:nth-child(3) { animation-delay: 0.15s; }
  .alumni-card:nth-child(4) { animation-delay: 0.20s; }
  .alumni-card:nth-child(5) { animation-delay: 0.25s; }
  .alumni-card:nth-child(6) { animation-delay: 0.30s; }

  @media (max-width: 600px) {
    .reco-grid { padding: 0.5rem 1rem 2rem; }
    .reco-header, .filter-tabs { padding-left: 1rem; padding-right: 1rem; }
  }
</style>

{% endblock %}

{% block content %}

<div class="reco-header">
  <h1>✦ Alumni recommandés</h1>
  <p>Personnes que vous pourriez connaître — basé sur votre promotion et votre filière</p>
</div>

<div class="filter-tabs">
  <button class="tab active" onclick="filterCards(this, 'all')">Tous</button>
  <button class="tab" onclick="filterCards(this, 'promo')">Même promotion</button>
  <button class="tab" onclick="filterCards(this, 'filiere')">Même filière</button>
  <button class="tab" onclick="filterCards(this, 'entreprise')">Même entreprise</button>
</div>

<div class="reco-grid" id="recoGrid">

{% if recommandations %}
{% for alumni in recommandations %}
<div class="alumni-card" data-reason="{{ alumni.raison_type }}">

```
  <div class="card-banner">
    <span class="shared-tag">
      {% if alumni.raison_type == 'promo' %}🎓 Promo {{ alumni.promotion }}
      {% elif alumni.raison_type == 'filiere' %}📚 {{ alumni.filiere }}
      {% elif alumni.raison_type == 'entreprise' %}🏢 {{ alumni.entreprise }}
      {% endif %}
    </span>

    {% if alumni.photo %}
      <img class="card-avatar" src="{{ alumni.photo.url }}" alt="{{ alumni.nom }}">
    {% else %}
      <div class="card-avatar-placeholder">
        {{ alumni.prenom|first|upper }}{{ alumni.nom|first|upper }}
      </div>
    {% endif %}
  </div>

  <div class="card-body">
    <div class="card-name">{{ alumni.prenom }} {{ alumni.nom }}</div>
    <div class="card-role">
      {% if alumni.poste %}{{ alumni.poste }}{% endif %}
      {% if alumni.entreprise %} · {{ alumni.entreprise }}{% endif %}
    </div>

    <div class="card-reason">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
      {% if alumni.raison_type == 'promo' %}Même promotion ({{ alumni.promotion }})
      {% elif alumni.raison_type == 'filiere' %}Même filière · {{ alumni.filiere }}
      {% elif alumni.raison_type == 'entreprise' %}Même entreprise
      {% endif %}
    </div>

    {% if alumni.competences %}
    <div class="skills-row">
      {% for comp in alumni.competences|slice:":3" %}
        <span class="skill-badge">{{ comp }}</span>
      {% endfor %}
    </div>
    {% endif %}

    <div class="card-actions">
      <button class="btn-follow" onclick="toggleFollow(this, {{ alumni.id }})">
        + Suivre
      </button>
      <a class="btn-profil" href="{% url 'profil_alumni' alumni.id %}">Voir</a>
    </div>
  </div>

</div>
{% endfor %}
```

{% else %}
<div class="empty-state">
<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
<circle cx="9" cy="7" r="4"/>
<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
<path d="M16 3.13a4 4 0 0 1 0 7.75"/>
</svg>
<p style="margin-top:1rem;">Aucune recommandation disponible pour l’instant.</p>
</div>
{% endif %}

</div>

{% endblock %}

{% block extra_js %}

<script>
function filterCards(btn, type) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.alumni-card').forEach(card => {
    card.style.display = (type === 'all' || card.dataset.reason === type) ? '' : 'none';
  });
}

function toggleFollow(btn, alumniId) {
  const isFollowing = btn.classList.contains('following');
  fetch(`/alumni/${alumniId}/suivre/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': '{{ csrf_token }}',
      'Content-Type': 'application/json',
    }
  })
  .then(res => res.json())
  .then(() => {
    btn.classList.toggle('following');
    btn.textContent = isFollowing ? '+ Suivre' : '✓ Suivi';
  })
  .catch(() => {
    btn.classList.toggle('following');
    btn.textContent = isFollowing ? '+ Suivre' : '✓ Suivi';
  });
}
</script>

{% endblock %}