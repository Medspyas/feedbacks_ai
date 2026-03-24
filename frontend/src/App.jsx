import {useState, useEffect} from 'react';
import {Sparkles, Star, Loader2, Check, Trash2} from 'lucide-react';


const App = () => {
  const [view, setView] = useState('form');
  const [status, setStatus] = useState('idle');
  const [rating, setRating] = useState(0);

  const [feedbacks, setFeedbacks] = useState([]);

  const [formData, setFormData] = useState({username: '', company_name: '',  category: '', content: '',});

  useEffect(() => {
    fetchFeedback();
  }, [])

  const fetchFeedback = async () => {
    try {
      const response = await fetch('/api/feedbacks/');
      const data = await response.json();
      setFeedbacks(data);      
    } catch (err) {
      console.error("Erreur lors de la récupération", err)
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
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
      setFeedbacks(feedbacks.filter(f => f.id !== id));
    } catch (err){
      console.error("Erreur suppression", err);
    }      
  };

  const getSentimentBadge = (status) => {
    if (status === 'analyzed') return { label: 'Analysé', cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'};
    return { label: 'En attente', cls: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20' };
  };


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
                <input 
                type="text" required placeholder='Nom du client'
                minLength={3} maxLength={50}
                value={formData.username}
                onChange={(e) => setFormData({... formData, username: e.target.value})}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all text-zinc-100 placeholder:text-zinc-600" 
                />
                <input 
                type="text" required placeholder='Entreprise'
                minLength={3} maxLength={50}
                value={formData.company_name}
                onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all text-zinc-100 placeholder:text-zinc-600" 
                />        

                <input 
                type="text" required placeholder='Catégorie'
                minLength={3} maxLength={20}
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all text-zinc-100 placeholder:text-zinc-600" 
                />  
              </div>
              

              <textarea
                required rows="4" placeholder="Ecrivez votre message... "
                minLength={10} 
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:border-indigo-500/50 focus:ring-indigo-500/50 outline-none transition-all resize-none text-zinc-100 placeholder:text-zinc-600"
              />

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
            {feedbacks.length === 0 ? (
              <p className='text-zinc-500 text-sm text-center py-12'>Aucun feedback pour le moment.</p>
            ) : (
              
            feedbacks.map((fb) => {
              const badge = getSentimentBadge(fb.status);
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
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2.5 py-1 rounded-full border ${badge.cls}`}>
                        {badge.label}
                      </span>

                      <button
                        onClick={() => handleDelete(fb._id)}
                        className="text-zinc-600 hover:text-red-400 transition-colors"
                        >
                          <Trash2 size={15}/>
                        </button>
                      </div>
                    </div>
                  

                    <p className="text-sm text-zinc-400 italic mb-4 ">"{fb.content}"</p>

                    {fb.ai_analysis && (
                      <div className="bg-indigo-500/5 rounded-xl p-4 border border-indigo-500/10">
                        <p className="text-xs font-medium text-indigo-300 mb-1">Analyse IA</p>
                        <p className="text-sm text-zinc-300">{fb.ai_analysis}</p>
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
