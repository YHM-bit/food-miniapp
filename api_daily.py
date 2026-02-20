@app.post("/api/daily")
def api_daily(x_telegram_init_data: str = Header(default="")):
    uid = uid_from_init(x_telegram_init_data)
    with LOCK:
        db = load_db()
        u = get_user(db, uid)
        apply_bonus(u)

        if not is_trial(u):
            if u.get("daily_paid") != today():
                if not charge(u, "daily"):
                    save_db(db)
                    raise HTTPException(402, "NO_TOKENS")
                u["daily_paid"] = today()

        dish = pick_daily(db, u)
        save_db(db)

    return {"ok": True, "dish": dish}
