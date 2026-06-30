export function CtaSection() {
    return (
        <section className="max-w-[1320px] mx-auto px-4 sm:px-7 pb-20">
            <div className="bg-[#E4FB52] rounded-[26px] p-10 sm:p-14 text-center">
                <h2 className="font-grotesk font-bold text-[36px] sm:text-[44px] tracking-[-0.03em] m-0 text-[#16181B]">
                    See VIGIA respond in real time
                </h2>
                <p className="text-center text-[17px] text-[#2C2E29] mt-4 mb-0 mx-auto max-w-[520px] leading-[1.55]">
                    Open the live operations dashboard: watch the map, the detection feed, and the
                    alert stream react to a simulated collision.
                </p>
                <button
                    type="button"
                    className="inline-flex mt-7 sm:mt-[30px] px-7 sm:px-[30px] py-4 rounded-[12px] bg-[#16181B] text-[#F4F3EE] font-semibold text-[16px] cursor-pointer"
                >
                    Open live dashboard →
                </button>
            </div>
        </section>
    );
}
