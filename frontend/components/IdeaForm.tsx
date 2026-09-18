"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  createProject,
  createRun,
} from "@/lib/projects";


export default function IdeaForm() {

  const router = useRouter();


  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);


  const textareaRef =
    useRef<HTMLTextAreaElement>(null);



  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const maxHeight = 160; // примерно 4 строки

    if (textarea.scrollHeight <= maxHeight) {
      textarea.style.height =
        `${textarea.scrollHeight}px`;

      textarea.style.overflowY = "hidden";
    } else {
      textarea.style.height =
        `${maxHeight}px`;

      textarea.style.overflowY = "auto";
    }

  }, [idea]);





  async function submit() {

    if (!idea.trim()) {
      return;
    }


    setLoading(true);


    try {

      const project =
        await createProject(
          "New Venture Analysis",
          idea,
        );


      const run =
        await createRun(
          project.id,
        );


      router.push(
        `/projects/${project.id}/runs/${run.id}`,
      );


    }
    finally {

      setLoading(false);

    }

  }





  return (

    <div
      className="
        w-full
        max-w-2xl
      "
    >


      <textarea
        ref={textareaRef}
        value={idea}
        onChange={(event) =>
          setIdea(event.target.value)
        }
        placeholder="Describe your startup idea..."
        rows={1}
        className="
          min-h-12
          max-h-40
          w-full

          resize-none
          overflow-hidden

          rounded-2xl

          border
          border-[var(--border)]

          bg-[var(--card)]

          px-5
          py-3

          text-xl
          leading-7

          text-[var(--foreground)]

          placeholder:text-[var(--muted)]

          outline-none

          transition-all
          duration-200

          focus:border-[var(--primary)]

          focus:ring-2
          focus:ring-[var(--primary)]
          focus:ring-opacity-30
        "
      />




      <button

        onClick={submit}

        disabled={
          loading
        }


        className="

          mt-4

          w-full

          rounded-2xl


          bg-[var(--primary)]

          px-6

          py-4


          text-xl

          font-semibold

          text-white


          transition


          hover:bg-[var(--primary-hover)]


          hover:shadow-lg


          active:scale-[0.98]


          disabled:cursor-not-allowed

          disabled:opacity-50

        "

      >

        {
          loading
            ? "Starting analysis..."
            : "Analyze Idea"
        }


      </button>



    </div>

  );

}