import HomeHeader from "@/components/main-page/HomeHeader";
import IdeaForm from "@/components/main-page/IdeaForm";


export default function Home() {
  return (
    <main
      className="
        relative
        flex
        min-h-screen
        flex-col
        items-center
        justify-center
        px-6
      "
    >
      <HomeHeader />

      <div
        className="
          w-full
          max-w-4xl
          text-center
        "
      >
        <div
          className="
            inline-flex
            rounded-full
            border
            px-4
            py-2
            text-lg
            font-medium
          "
          style={{
            color:
              "var(--primary)",
          }}
        >
          AI-powered venture analysis
        </div>

        <h1
          className="
            mt-8
            text-5xl
            font-bold
            tracking-tight
            sm:text-6xl
          "
        >
          Turn startup ideas into
          <br />
          actionable insights
        </h1>

        <p
          className="
            mx-auto
            mt-6
            max-w-2xl
            text-lg
            leading-8
          "
          style={{
            color:
              "var(--muted)",
          }}
        >
          Analyze your startup idea with a team
          of autonomous AI agents.
          Market research, customer analysis,
          competition review and business
          evaluation in one report.
        </p>

        <div
          className="
            mx-auto
            mt-10
            w-full
            max-w-2xl
          "
        >
          <IdeaForm />
        </div>
      </div>
    </main>
  );
}
