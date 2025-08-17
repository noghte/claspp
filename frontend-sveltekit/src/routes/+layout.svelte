<script>
import '$lib/app.css';
	import Navbar from './components/Navbar.svelte';
	import { base } from '$app/paths';

    // import Navbar from "/components/Navbar.svelte";
//     export async function load({ cookies }) {
//     return {
//       sessionid: await cookies.get('sessionid')
//     };
// }
  </script>
    <style lang="postcss">
      :global(html) {
        /* background-color: theme('colors.blue.100');
        direction: rtl; */
        margin: 1rem 1rem 1rem 1rem;
      }
    </style>

<!-- component -->
<div class="min-h-screen">

<Navbar />

<!-- <nav>
	<a href="{base}/">Home</a>
	<a href="{base}/about">About</a>
</nav> -->

<slot />

        <!-- <FooterSmall absolute="true" /> -->
</div>