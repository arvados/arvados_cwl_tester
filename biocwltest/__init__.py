# TODO check if file exists and do not push if yes


"""
Plan:


1. Zrób nowy projekt, który ma zniknąć po tygodniu
2. Uruchom w tym projekcie arvados-cwl-runner
    a. daj w subprocess żeby następna komenda uruchomiła się dopiero jak ten subprocess się skończy
    b. Zrób nazwę procesu
3. Za pomocą items wyszukaj w tym projekcie item, który będzie tym procesem. Sprawdź jaki jest jego status - jeżeli nie jest success to wtedy zwróć błąd. 
    sprawdź jakieś outputy i np. ich wielkość itd. 
4. Opcjonalnie uruchom inny cwl, który sprawdzi te outputy np. vcf ile ma lnijek, czy jest poprawny, czy ma indeks itd itp

pytest - niech uruchomi te testy parallelnie, po to żeby nie czekać i żeby na arvadosie już się liczyło

"""