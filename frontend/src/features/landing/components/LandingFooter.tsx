export function LandingFooter() {
    return (
        <footer className="border-t border-[#E6E4DC] bg-white">
            <div className="max-w-[1320px] mx-auto px-4 sm:px-7 py-7 flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-[8px] bg-[#16181B] flex items-center justify-center">
                        <div className="w-[11px] h-[11px] rounded-full border-2 border-[#E4FB52]" />
                    </div>
                    <span className="font-grotesk font-bold text-[15px] text-[#16181B]">VIGIA</span>
                    <span className="text-[#9A9C95] text-[13px] ml-1.5">
                        Vehicle Incident Guardian · PoC · IT · Aveiro
                    </span>
                </div>
                <span className="font-jetbrains text-[11.5px] text-[#9A9C95]">
                    Secured by CAPIF · Powered by 5G Core / NEF / CAMARA
                </span>
            </div>
        </footer>
    );
}
