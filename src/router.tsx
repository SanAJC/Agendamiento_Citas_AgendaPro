import { BrowserRouter, Routes, Route} from 'react-router-dom'
import IndexPage from './views/indexPage'
import FeaturesPage from './views/FeaturesPage'
import PricingPage from './views/PricingPage'
import ContactPage from './views/ContactPage'
import LoginPage from './views/LoginPage'
import RegisterPage from './views/RegisterPage'

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path='/' element={<IndexPage/>}/>
                <Route path='/features' element={<FeaturesPage/>}/>
                <Route path='/pricing' element={<PricingPage/>}/>
                <Route path='/contact' element={<ContactPage/>}/>
                <Route path='/login' element={<LoginPage/>}/>
                <Route path='/register' element={<RegisterPage/>}/>
            </Routes>
        </BrowserRouter>
    )
}
