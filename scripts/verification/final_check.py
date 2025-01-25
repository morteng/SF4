from scripts.verification import (  
    verify_production_ready,  
    verify_security,  
    verify_backups  
)  

def main():  
    checks = {  
        'Paths': verify_production_ready(),  
        'Security': verify_security(quick=True),  
        'Backups': verify_backups()  
    }  
    if all(checks.values()):  
        print("✅ System ready for deployment")  
    else:  
        print("❌ Deployment blocked - failed checks:")  
        [print(f"- {key}") for key, val in checks.items() if not val]

if __name__ == "__main__":
    main()
