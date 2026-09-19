import AuthForm from "@/components/AuthForm";


interface LoginPageProps {
  searchParams: Promise<{
    next?: string;
  }>;
}


export default async function LoginPage({
  searchParams,
}: LoginPageProps) {
  const params = await searchParams;

  return (
    <main
      className="
        flex
        min-h-screen
        items-center
        justify-center
        px-6
      "
    >
      <AuthForm
        mode="login"
        nextPath={params.next}
      />
    </main>
  );
}
