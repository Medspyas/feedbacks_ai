import {useState, useEffect, useRef} from 'react';
import {Sparkles, Star, Loader2, Check, Trash2} from 'lucide-react';


const App = () => {
  const [view, setView] = useState('form');
  const [status, setStatus] = useState('idle');
  const [rating, setRating] = useState(0);

  const [feedbacks, setFeedbacks] = useState([]);

  const [errors, setErrors] = useState({});

  const [formData, setFormData] = useState({username: '', company_name: '',  category: '', content: '',});

  const [searchTerm, setSearchTerm] = useState('')

  const [filters, setFilters] = useState({ priority: '', rating: 0 });

  useEffect(() => {
    fetchFeedback();
  }, [])

  const fetchFeedback = async () => {
    try {
      const response = await fetch('/api/feedbacks/');
      const data = await response.json();
      setFeedbacks(data);
      const sorted = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setFeedbacks(sorted); 
      setSearchTerm('');     
    } catch (err) {
      console.error("Erreur lors de la récupération", err)
    }
  };

  const validate = () => {
    const newErrors = {};
    if (formData.username.length < 3) newErrors.username = "Minimum 3 caractères";
    if (formData.company_name.length < 3) newErrors.company_name = "Minimum 3 caractères";
    if (formData.category.length < 3) newErrors.category = "Minimum 3 caractères";
    if (formData.content.length < 10) newErrors.content = "Minimum 10 caractères";
    if (rating === 0) newErrors.rating = "Veuillez sélectionner une note"
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setStatus('loading');

    try{
      const response = await fetch('/api/feedbacks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, rating })
      });

      if (response.ok) {
        await fetchFeedback();
        setStatus('success');
        setTimeout(() => { 
          setStatus('idle'); 
          setView('history'); 
          setRating(0); 
          setFormData({ username: '', company_name: '', category: '', content: '' });
        }, 
          1500);
        } 
    } catch (err) {
      setStatus('idle');
      console.error("Erreur IA", err);
    } 
  };

  const handleDelete = async (id) => {
    try {
      await fetch('/api/feedbacks/' + id, { method: 'DELETE' });
      setFeedbacks(feedbacks.filter(f => f._id !== id));
    } catch (err){
      console.error("Erreur suppression", err);
    }      
  };

  const getSentimentBadge = (status) => {
    if (status === 'analyzed') return { label: 'Analysé', cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'};
    return { label: 'En attente', cls: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20' };
  };

  const getPriorityBadge = (priority) => {
    if (priority === "high") return {label: 'Haute', cls: "bg-red-500/10 text-red-400 border-red-500/20"};
    if (priority === "medium") return {label: 'Moyenne', cls: "bg-amber-500/10 text-amber-400 border-amber-500/20"};
    return { label: "Basse", cls: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" }
  }

  const handleSearch = async (e) => {
    const value = e.target.value;
    setSearchTerm(value);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {

      try{
       const url = value
      ? `/api/feedbacks/?search=${encodeURIComponent(value)}`
      : '/api/feedbacks/';

      const response = await fetch(url);
      const data = await response.json();

      setFeedbacks(data);
    } catch (err) {
      console.error("Erreur recherche", err);
    }

    }, 300);

    
  };

  const filteredFeedbacks = feedbacks.filter(fb => {
    const matchPriority = filters.priority ? fb.priority === filters.priority : true;
    const matchRating = filters.rating ? fb.rating === filters.rating : true;
    return matchPriority && matchRating
  });

  


  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300 font-sans selection:bg-indigo-500/30 flex flex-col items-center pt-12 pb-24 px-6">
      {/* Header */}
      <nav className="w-full max-w-2xl flex justify-between items-center mb-16">
        <div className="flex items-center gap-2 text-zinc-100 font-semibold tracking-wide">
          <Sparkles size={18} className="text-indigo-400"/>
          <span>Feedback.ai</span>
        </div>
        <div className="flex gap-1 bg-zinc-900 p-1 rounded-lg border border-zinc-800">
          <button 
            onClick={() => setView('form')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${view === 'form' ? 'bg-zinc-800 text-zinc-100 shadow-sm': 'text-zinc-500 hover:text-zinc-300' }`}            
          >
            Nouveau
          </button>
          <button
            onClick={() => setView('history')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${view === 'history' ? 'bg-zinc-800 text-zinc-100 shadow-sm': 'text-zinc-500 hover:text-zinc-300' }`}   
          >
            Historique
          </button>
        </div>
      </nav>

      {/* main */}
      <main className="w-full max-w-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">

        {view === 'form' ? (
          <div className="space-y-8">
            <div className="text-center space-y-2">
              <h1 className="text-3xl font-semibold text-zinc-100 tracking-tight"> Analyser un retour client</h1>
              <p className="text-zinc-500 text-sm"> L'IA extrait instantanément le sentiment et les actions à mener.</p>
            </div>

            <form onSubmit={handleSubmit} className="bg-zinc-900/50 p-6 md:p-8 rounded-2xl border border-zinc-800/80 shadow-2xl space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                   <input 
                type="text" required placeholder='Nom du client'
                minLength={3} maxLength={50}
                value={formData.username}
                onChange={(e) => setFormData({... formData, username: e.target.value})}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all text-zinc-100 placeholder:text-zinc-600" 
                />
                {errors.username && <p className='text-red-400 text-xs mt-1'>{errors.username}</p>}
                </div>
               <div>
                <input 
                type="text" required placeholder='Entreprise'
                minLength={3} maxLength={50}
                value={formData.company_name}
                onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all text-zinc-100 placeholder:text-zinc-600" 
                />        
                {errors.company_name && <p className='text-red-400 text-xs mt-1'>{errors.company_name}</p>}
               </div>

            </div>
            
                <div>
                  <input 
                type="text" required placeholder='Catégorie'
                minLength={3} maxLength={20}
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all text-zinc-100 placeholder:text-zinc-600" 
                />
                {errors.category && <p className='text-red-400 text-xs mt-1'>{errors.category}</p>} 
                </div>
                 
              
              

              <textarea
                required rows="4" placeholder="Ecrivez votre message... "
                minLength={10} 
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all resize-none text-zinc-100 placeholder:text-zinc-600"
              />
              {errors.content && <p className='text-red-400 text-xs mt-1'>{errors.content}</p>}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-2">
                {/* rating */}
                <div className="flex gap-1.5">
                  {[1,2,3,4,5].map((star) => (
                    <button
                      key={star} type="button" onClick={() => setRating(star)}
                      className={`transition-colors ${star <= rating ? 'text-indigo-400': 'text-zinc-700 hover:text-zinc-500'}`}                    
                    >
                      <Star size={22} fill={star <= rating ? "currentColor" : "none"} strokeWidth={1.5} />
                    </button>
                  ))}
                </div>
                {errors.rating && <p className='text-red-400 text-xs mt-1'>{errors.rating}</p>}
                {/* button submit */}
                <button
                  type="submit" disabled={status !== 'idle'}
                  className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all disabled:opacity-70"
                >
                  {status === 'idle' && <><Sparkles size={16}/> Analyser avec L'IA</>}
                  {status === 'loading' && <><Loader2 size={16} className="animate-spin"/> Traitement ...</>}
                  {status === 'success' && <><Check size={16}/> Terminé</>}  
                  </button>
              </div>              
            </form>
          </div>
        ): (
          <div className="space-y-6">
            <h2 className="text-xl font-medium text-zinc-100">Analyse récentes</h2>

            <div className='relative'>
              <input 
              type="text"
              placeholder='Rechercher par nom, entreprise, contenu...'
              value={searchTerm}
              onChange={handleSearch}
              className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:b order-indigo-500/50 outline-none text-zinc-100 placeholder:text-zinc-600"
              />
              {searchTerm && (
                <button
                onClick={() => {
                  setSearchTerm('');
                  fetchFeedback();
                }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                >
                  x 
                </button>
              )}
            </div>

            <div className="flex gap-3">
  
            
            <select
              value={filters.priority}
              onChange={(e) => setFilters(f => ({ ...f, priority: e.target.value }))}
              className="text-xs px-3 py-2 rounded-xl border bg-zinc-900 border-zinc-800 text-zinc-400 outline-none cursor-pointer hover:border-zinc-600 transition-colors"
            >
              <option value="">Priorité</option>
              <option value="high">Haute</option>
              <option value="medium">Moyenne</option>
              <option value="low">Basse</option>
            </select>

            
            <select
              value={filters.rating}
              onChange={(e) => setFilters(f => ({ ...f, rating: Number(e.target.value) }))}
              className="text-xs px-3 py-2 rounded-xl border bg-zinc-900 border-zinc-800 text-zinc-400 outline-none cursor-pointer hover:border-zinc-600 transition-colors"
            >
                <option value={0}>Note</option>
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={3}>3</option>
                <option value={4}>4</option>
                <option value={5}>5</option>
            </select>

            
            {(filters.priority || filters.rating > 0) && (
              <button
                onClick={() => setFilters({ priority: '', rating: 0 })}
                className="text-xs px-3 py-2 rounded-xl border border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-600 transition-colors"
              >
                Réinitialiser
              </button>
            )}

          </div>

            {searchTerm && (
              <p className="text-xs text-zinc-500 -mt-4">
                {feedbacks.length} résultat{feedbacks.length > 1 ? 's': ''}
              </p>
            )}

            {feedbacks.length === 0 ? (
              <p className='text-zinc-500 text-sm text-center py-12'>Aucun feedback pour le moment.</p>
            ) : (
              
            filteredFeedbacks.map((fb) => {
              const badge = getSentimentBadge(fb.status);
              const priority = getPriorityBadge(fb.priority)
              return (
                <div key={fb._id} className="bg-zinc-900/30 p-6 rounded-2xl border border-zinc-800/80 hover:border-zinc-700 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-medium text-zinc-100">
                        {fb.username} <span className="text-zinc-600 font-normal">{fb.company_name}</span>

                      </h3>
                      <div className="flex items-center gap-1 mt-1 text-indigo-400">
                        <Star size={12} fill="currentColor"/> {fb.rating}/5
                      </div>

                      {fb.language && (
                        <span className='text-xs text-zinc-500'>Score {fb.satisfaction_score}/10</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2.5 py-1 rounded-full border ${badge.cls}`}>
                        {badge.label}
                      </span>

                      {fb.priority && (
                        <span className={`text-xs px-2.5 py-1 rounded-full border ${priority.cls}`}>
                          {priority.label}
                        </span>
                      )}

                      <button
                        onClick={() => handleDelete(fb._id)}
                        className="text-zinc-600 hover:text-red-400 transition-colors"
                        >
                          <Trash2 size={15}/>
                        </button>
                      </div>
                    </div>
                  

                    <p className="text-sm text-zinc-400 italic mb-4 ">"{fb.content}"</p>

                    {fb.keywords && fb.keywords.length > 0 && (
                      <div className='flex flex-wrap gap-2 mb-4'>
                        {fb.keywords.map((kw, i) => (
                          <span key={i} className='text-xs px-2 py-1 rounded-md bg-zinc-800 text-zinc-400 border border-zinc-700'>
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}

                    {fb.ai_analysis && (
                      <div className="bg-indigo-500/5 rounded-xl p-4 border border-indigo-500/10">
                        <p className="text-xs font-medium text-indigo-300 mb-1">Analyse IA</p>
                        <p className="text-sm text-zinc-300">{fb.ai_analysis}</p>

                        {fb.suggested_action && (
                          <p className='text-sm text-amber-400/80 border-t border-indigo-500/10 pt-2'>
                            <span className='font-medium'>Action recommandé: </span>
                            {fb.suggested_action}
                          </p>
                        )}

                        {fb.ai_response && (
                          <p className="text-sm text-zinc-400 mt-2 border-t border-indigo-500/10 pt-2">
                            <span className="text-indigo-300 font-medium"> Réponse suggérée: </span>
                            {fb.ai_response}
                          </p>
                        )}
                      </div>
                    )}
                </div>
              );
            })
          )}
        </div>
        
            

           
           

            
            
          
        )}
      </main>

    </div>
  );
};
export default App
