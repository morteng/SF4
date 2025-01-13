# Global Rules

1. **No direct Python in console commands**  
   Always create or update `.py` files, then run them with `/run my_script.py`.
2. **Inter-cycle communication**  
   Each cycle must output results (e.g., pass/fail metrics) that the next cycle can read.
3. **Logging**  
   All major actions must be logged (via `log_cycle_metrics.py` or appended to the dev log).
4. **Manager instructions override**  
   If `MANAGER.txt` says to pivot, you pivot. End of story.
5. **Backward compatibility**  
   Dont break the original automation flow if possible. This system should complement, not replace, the older structure (unless the older structure is a dumpster fire).
